# Copyright (c) ACSONE SA/NV 2022

from typing import Iterator

from odoo import _, api, models
from odoo.exceptions import UserError


class MisTaxReportBuilder(models.AbstractModel):
    _name = "mis.tax.report.builder"

    @api.model
    def _iter_account_tax_report_lines(
        self, lines: models.Model, level: int = 0
    ) -> Iterator[models.Model]:
        """Iterate account.tax.report.line, depth first."""
        for line in lines:
            yield line, level
            yield from self._iter_account_tax_report_lines(
                line.children_line_ids, level + 1
            )

    @api.model
    def _xmlid_from_object(self, o: models.Model) -> str:
        imd = (
            self.env["ir.model.data"]
            .sudo()
            .search([("model", "=", o._name), ("res_id", "=", o.id)], limit=1)
        )
        if not imd:
            return None
        return f"{imd.module}.{imd.name}"

    @api.model
    def _kpi_name_from_tax_report_line(self, line: models.Model) -> str:
        if line.code:
            return line.code
        xmlid = self._xmlid_from_object(line)
        if xmlid:
            return xmlid.replace(".", "_")
        return f"_{line.id}"

    @api.model
    def _populate_mis_report_template_from_tax_report(
        self, mis_report_template: models.Model, tax_report: models.Model
    ) -> None:
        """Populate the KPIs of a MIS Report template from an Odoo Tax Report.

        TODO

        * Instead of replacing all KPIs, update KPIs with the same name
          and remove those that do not exist any more in the Odoo report.
        * Link KPIs to predefined styles based on the level (styles to be added
          as data in this module).
        """
        mis_report_template.kpi_ids.unlink()
        for sequence, (report_line, _level) in enumerate(
            self._iter_account_tax_report_lines(tax_report.root_line_ids)
        ):
            kpi = self.env["mis.report.kpi"].new()
            kpi.name = self._kpi_name_from_tax_report_line(report_line)
            kpi.description = report_line.name
            kpi.sequence = sequence
            if report_line.tag_ids and report_line.formula:
                raise UserError(
                    _(
                        "Report line '{name}' has both Tags and a Forumla. "
                        "We don't grok this."
                    ).format(name=report_line.name),
                )
            if report_line.tag_name:
                # If the report line has tags, make an expression that gets the balance
                # of move lines with these tags over the period.
                kpi.expression = (
                    f'-balp[][("tax_tag_ids.name", "=", "+{report_line.tag_name}")]'
                    f'+balp[][("tax_tag_ids.name", "=", "-{report_line.tag_name}")]'
                )
            elif report_line.formula:
                # If the report line has a formula, we hope MIS Builder will grok it.
                kpi.expression = report_line.formula
            elif report_line.code:
                # If we have a code but no formula nor tags, we create an expression
                # that sums children.
                kpi.expression = " + ".join(
                    self._kpi_name_from_tax_report_line(cl)
                    for cl in report_line.children_line_ids
                )
            mis_report_template.kpi_ids |= kpi

    @api.model
    def _create_mis_report_template_from_tax_report(
        self, tax_report: models.Model
    ) -> models.Model:
        """Create a MIS Report template from an Odoo Tax Report."""
        mis_report = self.env["mis.report"].create(
            dict(name=f"{tax_report.name} {tax_report.country_id.name}")
        )
        mis_report._populate_from_tax_report(tax_report)
        return mis_report
