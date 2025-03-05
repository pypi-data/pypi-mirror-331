from .processor.dpir.processor_v2 import DPIRProcessor
from .processor.dru_rbpn_sr.processor_f3_v2 import DRURBPNSRF3Processor
from .processor.dru_rbpn_sr.processor_f5_v2 import DRURBPNSRF5Processor
from .processor.dru_asm_sr.processor_f3_v2 import DRUASMSRF3Processor
from .processor.dru_rbpn_deinter.processor_f3_gloss_v2 import (
    DRURBPNDEINTERF3GLOSSProcessor,
)
from .processor.fisf.processor_v2 import FISFProcessor
from .processor.color_resnet.processor_pre_v2 import COLORRESNETPREProcessor
from .processor.color_resnet.processor_post_v2 import COLORRESNETPOSTProcessor
from .processor.gg.processor_v2 import GGProcessor

__version__ = "2.2.2"
