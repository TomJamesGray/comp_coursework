import logging
from kivy.app import App
from stat_analysis.actions import base_action
from stat_analysis.generic_widgets.bordered import BorderedTable

logger = logging.getLogger(__name__)


class ViewData(base_action.BaseAction):
    type = "data.view_data"
    view_name = "View data"

    def __init__(self,output_widget,**kwargs):
        self.form = [
            {
                "group_name": "Data set",
                "inputs": [
                    {
                        "input_type": "combo_box",
                        "required": True,
                        "data_type":"dataset",
                        "form_name": "dataset",
                        "visible_name": "Data set"
                    }
                ]
            }
        ]
        self.output_widget = output_widget
        self.run_after_render = False

        if "dataset" in kwargs:
            # Dataset has been specified as a kwarg
            self.run_after_render = True
            self.form_outputs = {"dataset":kwargs["dataset"]}

    def render(self):
        super().render()
        if self.run_after_render:
            self.run(validate=False)

    def run(self,quiet=False,validate=True):
        logger.debug("Running action {}".format(self.type))
        if validate:
            if not self.validate_form():
                logger.warning("Form not validated, form errors: {}".format(self.form_errors))
                return False
            else:
                logger.debug("Form validated, form outputs: {}".format(self.form_outputs))
        vals = self.form_outputs
        cur_set = App.get_running_app().get_dataset_by_name(vals["dataset"])
        if cur_set == None:
            # This should never happen
            logger.error("Data set selected in combo box doesn't exist in app's data_sets")
            raise ValueError("Data set selected in combo box doesn't exist in app's data_sets")
        logger.debug("Using {} as cur_set".format(cur_set))
        if not quiet:
            self.result_output.clear_outputs()
            self.result_output.add_widget(BorderedTable(headers=cur_set.get_headers(),table_data=cur_set.get_data(),
                                                        row_default_height=30,row_force_default=True,for_scroller=True,
                                                        size_hint_x=1,size_hint_y=None))
