from odoo import api, fields, models, _
from datetime import date
from odoo.addons.queue_job.job import job
from odoo.exceptions import ValidationError
from ...services.contract_iban_change_process import ContractIbanChangeProcess
from ...otrs_services.update_ticket_with_error import UpdateTicketWithError


class ContractIbanChangeWizard(models.TransientModel):
    _name = "contract.iban.change.wizard"
    partner_id = fields.Many2one("res.partner")
    summary = fields.Char(required=True, translate=True, default="IBAN change")
    done = fields.Boolean(default=True)
    contract_ids = fields.Many2many("contract.contract", string="Contracts")
    available_contract_group_ids = fields.One2many(
        "contract.group",
        string="Available Contract Groups",
        compute="_compute_available_contract_group_ids",
    )
    contract_group_id = fields.Many2one(
        "contract.group",
        string="Contract Group",
        help="The contract groups that are available for the selected contracts. "
        "Keep empty to create a new contract group.",
    )
    account_banking_mandate_id = fields.Many2one(
        "account.banking.mandate",
        "Banking mandate",
        required=True,
    )

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        defaults["partner_id"] = self.env.context["active_id"]
        return defaults

    @api.multi
    def button_change(self):
        self.ensure_one()

        # Notification block: Write messages in the chatter of Contracts and Partner
        message_contract = _("Contract IBAN changed from {} to {}")
        contract_messages = []
        contract_names = []
        for contract in self.contract_ids:
            contract_messages.append(
                (
                    contract,
                    message_contract.format(
                        contract.mandate_id.partner_bank_id.acc_number,
                        self.account_banking_mandate_id.partner_bank_id.acc_number,
                    ),
                    contract.contract_group_id.code,
                )
            )
            contract_names.append(contract.name)

        message_partner = _(
            "IBAN changed from {} to {} in partner's contract/s '{}'"
        ).format(
            contract.mandate_id.partner_bank_id.acc_number,
            self.account_banking_mandate_id.partner_bank_id.acc_number,
            ", ".join(contract_names),
        )
        # Execution block: Change the mandate and group in contracts and create activity
        # If Group is defined validate the relation and add the field to write data
        # Else use create-contract strategy
        self._update_contracts()
        self._create_activity()
        self.enqueue_OC_iban_update()

        self.partner_id.message_post(message_partner)
        for contract, message_contract, contract_group in contract_messages:
            contract.message_post(message_contract)
            contract.message_post(
                _("Contract group changed from {} to {}").format(
                    contract_group, self.contract_group_id.code
                )
            )
        return True

    def _update_contracts(self):

        # Execution block: Change the mandate and group in contracts and create activity
        # If Group is defined validate the relation and add the field to write data
        # Else use create-contract strategy
        if not self.contract_group_id:
            self.contract_group_id = self.env[
                "contract.group"
            ].get_or_create_contract_group_id(
                self.contract_ids[0],
                new_group=True,
            )

        for contract in self.contract_ids:
            valid, error_message = self.contract_group_id.validate_contract_to_group(
                contract,
                self.account_banking_mandate_id,
            )
            if not valid:
                raise ValidationError(error_message)

        self.contract_ids.write(
            {
                "mandate_id": self.account_banking_mandate_id.id,
                "contract_group_id": self.contract_group_id.id,
            }
        )

    def _get_first_day_of_next_month(self, request_date):
        if request_date.month == 12:
            return date(request_date.year + 1, 1, 1)
        else:
            return date(request_date.year, request_date.month + 1, 1)

    def _create_activity(self):
        self.ensure_one()
        for contract in self.contract_ids:
            self.env["mail.activity"].create(
                {
                    "summary": self.summary,
                    "res_id": contract.id,
                    "res_model_id": self.env.ref("contract.model_contract_contract").id,
                    "user_id": self.env.user.id,
                    "activity_type_id": self.env.ref(
                        "somconnexio.mail_activity_type_iban_change"
                    ).id,
                    "done": self.done,
                    "date_done": date.today(),
                    "date_deadline": date.today(),
                }
            )

    def enqueue_OC_iban_update(self):
        self.env["contract.contract"].with_delay().update_subscription(
            self.contract_ids, "iban"
        )

    @job
    def run_from_api(self, **params):
        service = ContractIbanChangeProcess(self.env)
        try:
            service.run_from_api(**params)
        except ValidationError as error:
            ticket_id = params["ticket_id"]
            error = {
                "title": "Error en el canvi d'IBAN",
                "body": "Banc del nou IBAN desconegut: {}.".format(params.get("iban"))
                + "\nDesprés d'afegir el seu banc corresponent al registre "
                + "d'ODOO, torna a intentar aquesta petició.",
            }
            dynamic_fields_dct = {"ibanKO": 1}
            update_ticket = UpdateTicketWithError(ticket_id, error, dynamic_fields_dct)

            update_ticket.run()

    @api.onchange("account_banking_mandate_id", "contract_ids")
    def _compute_available_contract_group_ids(self):
        if not self.contract_ids or not self.account_banking_mandate_id:
            self.available_contract_group_ids = []
            return

        self.available_contract_group_ids = (
            self.env["contract.group"]
            .search([("partner_id", "=", self.contract_ids[0].partner_id.id)])
            .filtered(
                lambda x: x.validate_contract_to_group(
                    self.contract_ids[0], mandate_id=self.account_banking_mandate_id
                )[0]
            )
        )
        self.contract_group_id = (
            self.available_contract_group_ids[0]
            if self.available_contract_group_ids
            else False
        )
