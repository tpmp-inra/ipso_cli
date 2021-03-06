import numpy as np

import logging

logger = logging.getLogger(__name__)

from ipapi.base.ip_common import get_hr_channel_name, CHANNELS_BY_SPACE, HSV, LAB, RGB
from ipapi.base.ipt_abstract import IptBase
from ipapi.base.ipt_abstract_analyzer import IptBaseAnalyzer
from ipapi.base.ip_common import ToolFamily


class IptImageStats(IptBaseAnalyzer):
    def build_params(self):
        self.add_source_selector(default_value="source")
        self.add_color_space(default_value="LAB")
        self.add_text_output(
            is_single_line=True, name="channel_1_avg", desc="-", default_value="-"
        )
        self.add_text_output(
            is_single_line=True, name="channel_1_std", desc="-", default_value="-"
        )
        self.add_text_output(
            is_single_line=True, name="channel_2_avg", desc="-", default_value="-"
        )
        self.add_text_output(
            is_single_line=True, name="channel_2_std", desc="-", default_value="-"
        )
        self.add_text_output(
            is_single_line=True, name="channel_3_avg", desc="-", default_value="-"
        )
        self.add_text_output(
            is_single_line=True, name="channel_3_std", desc="-", default_value="-"
        )

    def process_wrapper(self, **kwargs):
        """
        Image statistics:
        Displays image color statistics
        Real time : True

        Keyword Arguments (in parentheses, argument name):
            * Select source file type (source_file): no clue
            * Color space (color_space): no clue
        --------------
            * output  (channel_1_avg): -
            * output  (channel_1_std): -
            * output  (channel_2_avg): -
            * output  (channel_2_std): -
            * output  (channel_3_avg): -
            * output  (channel_3_std): -
        """
        wrapper = self.init_wrapper(**kwargs)
        if wrapper is None:
            return False

        res = False
        try:
            self.data_dict = {}
            color_space = self.get_value_of("color_space")

            if color_space == "HSV":
                channels = CHANNELS_BY_SPACE[HSV]
            elif color_space == "LAB":
                channels = CHANNELS_BY_SPACE[LAB]
            elif color_space == "RGB":
                channels = CHANNELS_BY_SPACE[RGB]
            else:
                return

            img = wrapper.current_image
            wrapper.store_image(img, "used_source")

            text_overlay = []
            for i, channel in enumerate(channels):
                cc = wrapper.get_channel(img, channel=channel)
                wrapper.store_image(cc, f"c{i+1}")
                avg_, std_ = wrapper.get_channel_stats(channel=cc)
                p_avg = self.find_by_name(f"channel_{i+1}_avg")
                p_avg.update_output(
                    label_text=f"Average pixel value for {get_hr_channel_name(channel)}",
                    output_value=f"{avg_:.2f}",
                )
                self.add_value(
                    f"Average pixel value for {get_hr_channel_name(channel)}",
                    f"{avg_:.2f}",
                    True,
                )
                text_overlay.append(f"Avg value: {get_hr_channel_name(channel)}: {avg_:.2f}")
                p_std = self.find_by_name(f"channel_{i+1}_std")
                p_std.update_output(
                    label_text=f"Standard deviation for {get_hr_channel_name(channel)}",
                    output_value=f"{std_}",
                )
                self.add_value(
                    f"Standard deviation for {get_hr_channel_name(channel)}", f"{std_}", True
                )
                text_overlay.append(f"Std value: {get_hr_channel_name(channel)}: {std_:.2f}")
            text_overlay = "\n".join(text_overlay)

            _mosaic_data = np.array([["c1", "c2"], ["used_source", "c3"]])
            h, w = img.shape[:2]
            w *= 2
            h *= 2
            canvas = wrapper.build_mosaic((h, w, 3), _mosaic_data)
            wrapper.store_image(canvas, "mosaic_out", text_overlay=text_overlay)

            res = True

        except Exception as e:
            wrapper.error_holder.add_error(
                new_error_text=f'Failed to process {self. name}: "{repr(e)}"',
                new_error_level=35,
                target_logger=logger,
            )
            res = False
        else:
            pass
        finally:
            self.result = len(self.data_dict) > 0
            return res

    @property
    def name(self):
        return "Image statistics"

    @property
    def real_time(self):
        return True

    @property
    def result_name(self):
        return "none"

    @property
    def output_kind(self):
        return "none"

    @property
    def use_case(self):
        return [ToolFamily.FEATURE_EXTRACTION]

    @property
    def description(self):
        return "Displays image color statistics"
