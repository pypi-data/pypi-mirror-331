from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SubscriptionRequest(models.Model):
    _inherit = "subscription.request"

    mandate_id = fields.Many2one(
        "account.banking.mandate",
        string="Direct Debit Mandate",
        ondelete="restrict",
        check_company=True,
        readonly=False,
        domain="[('state', 'in', ('draft', 'valid')), ('partner_id', '=', partner_id)]",
    )
    mandate_required = fields.Boolean(
        related="payment_mode_id.payment_method_id.mandate_required",
    )
    mandate_approved = fields.Boolean(
        required=True, default=False, string="Approved creation of new mandate"
    )

    def create_invoice(self, partner):
        if self.mandate_required:
            existing_rpb = self._get_existing_rpb()
            if not existing_rpb:
                existing_rpb = self._create_bank()
            if existing_rpb and not existing_rpb.mandate_ids:
                self._validate_mandate_creation()
                self.mandate_id = self._create_mandate(existing_rpb)
        return super().create_invoice(partner)


    def _validate_mandate_creation(self):
        if not self.partner_id:
            raise ValidationError(_("Must assign a valid cooperator."))
        if not self.mandate_approved:
            raise ValidationError(_("Must check the mandate creation."))
        if not self.iban:
            raise ValidationError(_("Must assign a valid iban."))

    def _create_mandate(self, rpb):
        return self.env["account.banking.mandate"].with_company(self.company_id.id).create({
            "format": "sepa",
            "type": "recurrent",
            "state": "valid",
            "signature_date": self.date,
            "partner_bank_id": rpb.id,
            "partner_id": self.partner_id.id,
            "company_id": self.company_id.id,
        })

    def get_invoice_vals(self, partner):
        vals = super().get_invoice_vals(partner)
        vals["mandate_id"] = self.mandate_id.id
        return vals

    def _get_existing_rpb(self):
        return self.partner_id.bank_ids.filtered(lambda rpb: rpb.acc_number == self.iban and rpb.company_id == self.company_id.id)

    def _create_bank(self):
        return self.env["res.partner.bank"].create(
            {
                "partner_id": self.partner_id.id,
                "acc_number": self.iban,
                "company_id": self.company_id.id
            }
        )

    def get_mandate_values(self):
        return 

    @api.onchange("partner_id")
    def onchange_partner(self):
        super().onchange_partner()
        self.mandate_id = False
