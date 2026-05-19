from .m01_random import M01_RandomSelector
from .m03_coretab import M03_CoreTabSelector
from .m04_substrat import M04_SubStratSelector
from .m05_craig import M05_CraigSelector
from .m06_gradmatch import M06_GradMatchSelector
from .m07_glister import M07_GlisterSelector
from .m08_datamaps import M08_DataMapsSelector
from .m09_forgetting import M09_ForgettingSelector
from .m10_svp import M10_SVPSelector
from .m11_moderate_ds import M11_ModerateDSSelector
from .m12_dataset_condensation import M12_DatasetCondensationSelector
from .m13_distribution_matching import M13_DistributionMatchingSelector
from .m14_tdcoler import M14_TDColERSelector
from .m15_tabkde import TabKDESelector

# Registry map for easy loading by name in the Factory loop
METHOD_REGISTRY = {
    "M01_Random": M01_RandomSelector,
    "M03_CoreTab": M03_CoreTabSelector,
    "M04_SubStrat": M04_SubStratSelector,
    "M05_CRAIG": M05_CraigSelector,
    "M06_GradMatch": M06_GradMatchSelector,
    "M07_GLISTER": M07_GlisterSelector,
    "M08_DataMaps": M08_DataMapsSelector,
    "M09_Forgetting": M09_ForgettingSelector,
    "M10_SVP": M10_SVPSelector,
    "M11_ModerateDS": M11_ModerateDSSelector,
    "M12_DC": M12_DatasetCondensationSelector,
    "M13_DM": M13_DistributionMatchingSelector,
    "M14_TDColER": M14_TDColERSelector,
    "M15_TabKDE": TabKDESelector,
}
