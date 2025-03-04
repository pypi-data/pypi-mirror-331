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
    contract_group_id = fields.Many2one("contract.group", string="Contract Group")
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
        contract_names = []
        for contract in self.contract_ids:
            contract.message_post(
                message_contract.format(
                    contract.mandate_id.partner_bank_id.acc_number,
                    self.account_banking_mandate_id.partner_bank_id.acc_number,
                )
            )
            contract_names.append(contract.name)

        message_partner = _("IBAN changed from {} to {} in partner's contract/s '{}'")
        self.partner_id.message_post(
            message_partner.format(
                contract.mandate_id.partner_bank_id.acc_number,
                self.account_banking_mandate_id.partner_bank_id.acc_number,
                ", ".join(contract_names),
            )
        )

        # Execution block: Change the mandate and group in contracts and create activity
        # If Group is defined validate the relation and add the field to write data
        # Else use create-contract strategy
        if not self.contract_group_id:
            self.contract_group_id = self.env["contract.group"].get_contract_group_id(
                self.contract_ids[0],
                self.account_banking_mandate_id,
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
        self._create_activity()

        # Integrations block: Change the mandate in the invoicing system
        self.enqueue_OC_iban_update()
        return True

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
                    ).id,  # noqa
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
