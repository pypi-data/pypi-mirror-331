"""

Submodules containing `DICOM <https://www.dicomstandard.org/>`_ related functionalities.
"""
from __future__ import annotations
import imfusion._bindings
import numpy
import typing
__all__ = ['GeneralEquipmentModuleDataComponent', 'RTStructureDataComponent', 'ReferencedInstancesComponent', 'SourceInfoComponent', 'load_file', 'load_folder', 'rtstruct_to_labelmap', 'save_file', 'save_folder', 'save_rtstruct', 'set_pacs_client_config']
class GeneralEquipmentModuleDataComponent(imfusion._bindings.DataComponentBase):
    anatomical_orientation_type: str
    device_serial_number: str
    gantry_id: str
    institution_address: str
    institution_name: str
    institutional_departmentname: str
    manufacturer: str
    manufacturers_model_name: str
    software_versions: str
    spatial_resolution: float
    station_name: str
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    def __init__(self) -> None:
        ...
class RTStructureDataComponent(imfusion._bindings.DataComponentBase):
    """
    
    	DataComponent for PointClouds loaded from a DICOM RTStructureSet.
    
    	Provides information about the original structure/grouping of the points.
    	See RTStructureIoAlgorithm for details about how RTStructureSets are loaded.
    	
    	.. warning::
    		Since this component uses fixed indices into the PointCloud's points structure,
    		it can only be used if the PointCloud remains unchanged!
    """
    class Contour:
        """
        Represents a single item in the original 'Contour Sequence' (3006,0040).
        """
        __hash__: typing.ClassVar[None] = None
        length: int
        start_index: int
        type: RTStructureDataComponent.GeometryType
        @staticmethod
        def _pybind11_conduit_v1_(*args, **kwargs):
            ...
        def __eq__(self, arg0: RTStructureDataComponent.Contour) -> bool:
            ...
    class GeometryType:
        """
        Defines how the points of a contour should be interpreted.
        
        Members:
        
          POINT
        
          OPEN_PLANAR
        
          CLOSED_PLANAR
        
          OPEN_NONPLANAR
        """
        CLOSED_PLANAR: typing.ClassVar[RTStructureDataComponent.GeometryType]  # value = <GeometryType.CLOSED_PLANAR: 2>
        OPEN_NONPLANAR: typing.ClassVar[RTStructureDataComponent.GeometryType]  # value = <GeometryType.OPEN_NONPLANAR: 3>
        OPEN_PLANAR: typing.ClassVar[RTStructureDataComponent.GeometryType]  # value = <GeometryType.OPEN_PLANAR: 1>
        POINT: typing.ClassVar[RTStructureDataComponent.GeometryType]  # value = <GeometryType.POINT: 0>
        __members__: typing.ClassVar[dict[str, RTStructureDataComponent.GeometryType]]  # value = {'POINT': <GeometryType.POINT: 0>, 'OPEN_PLANAR': <GeometryType.OPEN_PLANAR: 1>, 'CLOSED_PLANAR': <GeometryType.CLOSED_PLANAR: 2>, 'OPEN_NONPLANAR': <GeometryType.OPEN_NONPLANAR: 3>}
        @staticmethod
        def _pybind11_conduit_v1_(*args, **kwargs):
            ...
        def __eq__(self, other: typing.Any) -> bool:
            ...
        def __getstate__(self) -> int:
            ...
        def __hash__(self) -> int:
            ...
        def __index__(self) -> int:
            ...
        def __init__(self, value: int) -> None:
            ...
        def __int__(self) -> int:
            ...
        def __ne__(self, other: typing.Any) -> bool:
            ...
        def __repr__(self) -> str:
            ...
        def __setstate__(self, state: int) -> None:
            ...
        def __str__(self) -> str:
            ...
        @property
        def name(self) -> str:
            ...
        @property
        def value(self) -> int:
            ...
    class ROIGenerationAlgorithm:
        """
        Defines how the RT structure was generated
        
        Members:
        
          UNKNOWN
        
          AUTOMATIC
        
          SEMI_AUTOMATIC
        
          MANUAL
        """
        AUTOMATIC: typing.ClassVar[RTStructureDataComponent.ROIGenerationAlgorithm]  # value = <ROIGenerationAlgorithm.AUTOMATIC: 1>
        MANUAL: typing.ClassVar[RTStructureDataComponent.ROIGenerationAlgorithm]  # value = <ROIGenerationAlgorithm.MANUAL: 3>
        SEMI_AUTOMATIC: typing.ClassVar[RTStructureDataComponent.ROIGenerationAlgorithm]  # value = <ROIGenerationAlgorithm.SEMI_AUTOMATIC: 2>
        UNKNOWN: typing.ClassVar[RTStructureDataComponent.ROIGenerationAlgorithm]  # value = <ROIGenerationAlgorithm.UNKNOWN: 0>
        __members__: typing.ClassVar[dict[str, RTStructureDataComponent.ROIGenerationAlgorithm]]  # value = {'UNKNOWN': <ROIGenerationAlgorithm.UNKNOWN: 0>, 'AUTOMATIC': <ROIGenerationAlgorithm.AUTOMATIC: 1>, 'SEMI_AUTOMATIC': <ROIGenerationAlgorithm.SEMI_AUTOMATIC: 2>, 'MANUAL': <ROIGenerationAlgorithm.MANUAL: 3>}
        @staticmethod
        def _pybind11_conduit_v1_(*args, **kwargs):
            ...
        def __eq__(self, other: typing.Any) -> bool:
            ...
        def __getstate__(self) -> int:
            ...
        def __hash__(self) -> int:
            ...
        def __index__(self) -> int:
            ...
        def __init__(self, value: int) -> None:
            ...
        def __int__(self) -> int:
            ...
        def __ne__(self, other: typing.Any) -> bool:
            ...
        def __repr__(self) -> str:
            ...
        def __setstate__(self, state: int) -> None:
            ...
        def __str__(self) -> str:
            ...
        @property
        def name(self) -> str:
            ...
        @property
        def value(self) -> int:
            ...
    color: numpy.ndarray[numpy.float64[3, 1]]
    contours: list[RTStructureDataComponent.Contour]
    generation_algorithm: RTStructureDataComponent.ROIGenerationAlgorithm
    referenced_frame_of_reference_UID: str
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    def __init__(self) -> None:
        ...
class ReferencedInstancesComponent(imfusion._bindings.DataComponentBase):
    """
    
    	DataComponent to store DICOM instances that are referenced by the dataset.
    
    	A DICOM dataset can reference a number of other DICOM datasets that are somehow related.
    	The references in this component are determined by the ReferencedSeriesSequence.
    """
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    def __init__(self) -> None:
        ...
    @typing.overload
    def is_referencing(self, arg0: SourceInfoComponent) -> bool:
        """
        		Returns true if the instances of the given SourceInfoComponent are referenced by this component.
        
        		The instances and references have to only intersect for this to return true.
        		This way, e.g. a segmentation would be considered referencing a CT if it only overlaps in a view
        		slices.
        """
    @typing.overload
    def is_referencing(self, arg0: imfusion._bindings.SharedImageSet) -> bool:
        """
        		Convenient method that calls the above method with SourceInfoComponent of sis.
        
        		Only returns true if all elementwise SourceInfoComponents are referenced.
        """
class SourceInfoComponent(imfusion._bindings.DataComponentBase):
    sop_class_uids: list[str]
    sop_instance_uids: list[str]
    source_uris: list[str]
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    def __init__(self) -> None:
        ...
def load_file(file_path: str) -> list:
    """
    Load a single file as DICOM.
    
    Depending on the SOPClassUID of the DICOM file, this can result in:
    
    - a 2D or 3D :class:`~imfusion.SharedImageSet` containing one or multiple frames
    - a segmentation labelmap (i.e. a 8-bit :class:`~imfusion.SharedImageSet` with a :class:`~imfusion.LabelDataComponent`)
    - a RT Structure Set (i.e. a :class:`~imfusion.PointCloud` with a :class:`~imfusion.RTStructureDataComponent`)
    
    For regular images, usually only one result is generated.
    If not it is usually an indication that the file could not be entirely reconstructed as a volume
    (e.g. the spacing between slices is not uniform).
    
    For segmentations, multiple labelmaps will be returned if labels overlap (i.e. one pixel has at least 2 labels).
    
    For RT Structure Sets, one :class:`~imfusion.PointCloud` is returned per structure.
    """
def load_folder(folder_path: str, recursive: bool = True, ignore_non_dicom: bool = True) -> list:
    """
    Load all DICOM files from a folder.
    
    Generally this produces one dataset per DICOM series, however, this might not always be the case.
    Check :class:`~imfusion.ImageInfoDataComponent` for the actual series UID.
    
    See :func:`imfusion.dicom.load_file` for a list of datasets that can be generated.
    
    Either a path to a local folder or a URL is accepted. URLs support the file:// and pacs:// schemes.
    To load a series from PACS, use an URL with the following format:
    ``pacs://<hostname>:<port>/<PACS AE title>?series=<series instance uid>&study=<study instance uid>``
    To receive DICOMs from the PACS, a temporary server will be started on the port defined
    by :func:`imfusion.dicom.set_pacs_client_config`.
    
    Args:
    	folder_path (str): A path to a folder or an URL.
    	recursive (bool): Whether subfolders should be scanned recursively for all DICOM files.
    	ignore_non_dicom(bool): Whether files without a valid DICOM header should be ignored.
    							This is usually faster and produces less warnings/errors,
    							but technically the DICOM header is optional and might be missing.
    							This is very rare though.
    """
def rtstruct_to_labelmap(rtstruct_set: list[imfusion._bindings.PointCloud], referenced_image: imfusion._bindings.SharedImageSet, combine_label_maps: bool = False) -> list[imfusion._bindings.SharedImageSet]:
    """
    Algorithm to convert a :class:`~imfusion.PointCloud` with a :class:`~imfusion.RTStructureDataComponent` datacomponent to a labelmap.
    
    This is currently only supported for CLOSED_PLANAR contours in :class:`~imfusion.RTStructureDataComponent`.
    The algorithm requires a reference volume that determines the size of the labelmap.
    Each contour is expected to be planar on a slice in the reference volume.
    This algorithm works best when using the volume that is referenced by the original DICOM RTStructureDataSet
    (see :py:attr:`imfusion.RTStructureDataComponent.referenced_frame_of_reference_UID`).
    
    Returns one labelmap per input RT Structure.
    """
def save_file(image: imfusion._bindings.SharedImageSet, file_path: str, referenced_image: imfusion._bindings.SharedImageSet = None) -> None:
    """
    Save an image as a single DICOM file.
    
    The SOP Class that is used for the export is determined based on the modality of the image.
    For example, CT images will be exported as 'Enhanced CT Image Storage' and LABEL images as 'Segmentation Storage'.
    
    When exporting volumes, note that older software might not be able to load them. Use :func:`imfusion.dicom.save_folder` instead.
    
    Optionally, the generated DICOMs can also reference another DICOM image, which is passed with the `referenced_image` argument.
    This `referenced_image` must have been loaded from DICOM and/or contain a elementwise :class:`~imfusion.SourceInfoComponent` and
    a :class:`~imfusion.ImageInfoDataComponent` contain a valid series instance UID.
    With such a reference, other software can determine whether different DICOMs are related.
    This is especially important when exporting segmentations with modality LABEL.
    The exported segmentations must reference the data that was used to generate the segmentation.
    If this reference is missing, the exported segmentations cannot be loaded in some software.
    
    When exporting segmentations, only the slices containing non-zero labels will be exported. After re-importing the
    file, it therefore might have a different number of slices.
    
    For saving RT Structures, see :func:`imfusion.dicom.save_rtstruct`.
    
    Args:
    	image (imfusion.SharedImageSet): The image to export
    	file_path (str): File to write the resulting DICOM to. Existing files will be overwritten!
    	referenced_image (imfusion.SharedImageSet): An optional image that the exported image should reference.
    
    Warning:
    	At the moment, only exporting single frame CT and MR volumes is well supported. Since DICOM is an extensive
    	standard, any other kind of image might lead to a non-standard or invalid DICOM.
    """
def save_folder(image: imfusion._bindings.SharedImageSet, folder_path: str, referenced_image: imfusion._bindings.SharedImageSet = None) -> None:
    """
    Save an image as a DICOM folder containing potentially multiple files.
    
    The SOP Class that is used for the export is determined based on the modality of the image.
    For example, CT images will be exported as 'CT Image Storage'.
    
    Works like :func:`imfusion.dicom.save_file` except for using different SOP Class UIDs.
    """
@typing.overload
def save_rtstruct(labelmap: imfusion._bindings.SharedImageSet, referenced_image: imfusion._bindings.SharedImageSet, file_path: str) -> None:
    """
    	Save a labelmap as a RT Structure Set.
    
    	The contours of a label inside the labelmap will be used as a contour in the RT Structure.
    	Each slice of the labelmap generates seperate contours (RT Structure does not support 3D contours).
    """
@typing.overload
def save_rtstruct(rtstruct_set: list[imfusion._bindings.PointCloud], referenced_image: imfusion._bindings.SharedImageSet, file_path: str) -> None:
    """
    	Save a list of :class:`~imfusion.PointCloud` as a RT Structure Set.
    
    	Each :class:`~imfusion.PointCloud` must provide a :class:`~imfusion.RTStructureDataComponent`.
    """
def set_pacs_client_config(ae_title: str, port: int) -> None:
    """
    	Set the client configuration when connecting to a PACS.
    
    	To receive DICOMs from a PACS server, the AE title and port needs to be registered
    	with the PACS as well (vendor specific and *not* done by this function!).
    
    	Warning:
    		The values will be persisted on the system and will be restored when the application is restarted.
    """
