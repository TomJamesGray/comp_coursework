import logging
from kivy.uix.label import Label
from kivy.app import App
from stat_analysis.form_inputs import combo_box,check_box,numeric_bounded,numeric,file,string
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.splitter import Splitter
from kivy.uix.button import Button

logger = logging.getLogger(__name__)

form_input_maps = {
    "combo_box":combo_box.FormDropDown,
    "check_box":check_box.FormCheckBox,
    "numeric_bounded":numeric_bounded.FormNumericBounded,
    "numeric":numeric.FormNumeric,
    "file":file.FormFile,
    "string":string.FormString
}


class BaseAction(object):
    def render(self):
        """
        This is the basic method that renders an action by going through the form property.
        The form property should be structured as a list of form groups. The form group is purely
        for aesthetic reasons currently. The following is an example of a form group:
         {
            "group_name":"Regression",
            "inputs":[
                {
                    "input_type": "check_box",
                    "form_name": "regression",
                    "visible_name": "Regression"
                }
            ]
        }
        The inputs property is a list of dictionaries defining each individual input. Input_type is
        the type of input to be used and will be looked up in form_input_maps. Form name is the
        key for the value in the form_outputs that will be set by the validate method. Visible name
        is the label that will be shown to the user
        :return:
        """
        logger.info("Rendering action {}".format(self.type))
        form_layout = GridLayout(cols=1,padding=(5,5),spacing=(10,10),width=220,size_hint=(None,None))
        form_layout.bind(minimum_height=form_layout.setter("height"))
        self.form_items = []
        for group in self.form:
            group_lbl = Label(text=group["group_name"],size_hint=(1,None),
                              height=30,font_size="22",color=App.get_running_app().accent_col)
            group_lbl.bind(size=group_lbl.setter("text_size"))
            form_layout.add_widget(group_lbl)

            for item in group["inputs"]:
                try:
                    cls = form_input_maps[item["input_type"]]
                except KeyError:
                    logger.error("Form input {} not found in form_input_maps".format(item["input_type"]))
                    # Go to next form input
                    continue
                # Give the form widget the whole dict so it can parse the data there
                logger.info("Adding form item {} for {}".format(cls,item["form_name"]))
                form_cls = cls(item,parent_action=self)
                form_layout.add_widget(form_cls)
                self.form_items.append(form_cls)

        scroller = ScrollView(size_hint=(None,1),width=220)
        scroller.add_widget(form_layout)
        self.output_widget.add_widget(scroller)

        # Create the generic output area
        result_output = ResultOutputWidget(cols=1)
        self.output_widget.add_widget(result_output)
        # Add property so that the result output can be added to when the action is run
        self.result_output = result_output

    def validate_form(self):
        """
        Validates the form based on the input dictionaries for each form input,
        handles exceptions thrown by the individual form items on get_val method
        and validation based on input dict criterion.
        If the form is valid the values and form_name's of each input is stored in
        a dict in form_inputs, if the form is invalid the errors are stored in
        form_errors
        :return: Boolean depending on whether form was filled out properly or not
        """
        output = {}
        errors = []
        for item in self.form_items:
            logger.info("Validating {}".format(item))
            try:
                # Handle errors that may be found in get_val method, ie can't cast to float
                # in numeric input
                val = item.get_val()
            except Exception as e:
                errors.append(str(e))
                logger.warning(errors[-1])
                continue

            if item.input_dict["required"] and val == None:
                errors.append("Field {} is required".format(item.input_dict["form_name"]))
                logger.warning(errors[-1])

            # Add the input value to the output dictionary
            output[item.input_dict["form_name"]] = val

        if errors == []:
            self.form_outputs = output
            return True
        else:
            self.form_errors = errors
            return False


class ResultOutputWidget(GridLayout):
    pass