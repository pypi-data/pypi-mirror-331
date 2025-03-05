import pathlib
import warnings
from typing import Optional
from xml.etree import ElementTree

import numpy
import tifffile
import zarr
from dask import array as darray
from napari.types import LayerDataTuple
from napari.utils import Colormap
from napari.utils.notifications import WarningNotification

# from typing import TYPE_CHECKING
# if TYPE_CHECKING:
#     import napari


def load_img(
    path: str | pathlib.Path,
    modality: Optional[str] = None,
    load_mem: bool = False,
) -> list[LayerDataTuple]:
    """
    Load an image file and convert it to a list of image layers for use in napari.

    Parameters:
    path (str | pathlib.Path): The path to the image file.
    modality (Optional[str]): The modality of the image (e.g., "BF" for Brightfield,
        "IF" for Immunofluorescence). If None, the modality will be inferred.
    load_mem (bool): Whether to load the image into memory.

    Returns:
    list[napari.types.LayerDataTuple]: A list of LayerDataTuple containing the
        image layer information.
    """

    if isinstance(path, str):
        path = pathlib.Path(path)

    zarray, int_scale, _ = read_img(path, load_mem)  # return modality
    if modality is None:
        modality = _
    else:
        print(modality)
        print(_)
        if modality == _:
            print("Selected modality matches expectations")
        else:
            print("Something is off!")
    md = read_md(path, modality)
    md["int_scale"] = int_scale

    print("Image was initiliased")

    if modality == "BF":
        print("Brightfield")
        img_layer_data = [
            (
                zarray,
                {
                    "name": path.stem,
                    "scale": md["res_scale"],
                    "metadata": md,
                    "contrast_limits": [0, md["int_scale"]],
                },
                "image",
            )
        ]
    else:
        print("Fluorescence")
        img_layer_data = []
        for index, (target, col) in enumerate(md["colmap_channels"].items()):
            md["dye"] = target
            layer = md["dye"]
            if md["new_format"] == True:
                md["biomarker"] = md["fluor_to_marker"][target]
                layer = md["biomarker"]
            cmap = Colormap(
                colors=numpy.array([(0, 0, 0, 1), col + (1,)]), name=target
            )

            channel_zarray = [array[index, :, :] for array in zarray]

            img_layer_data.append(
                (
                    channel_zarray,
                    {
                        "name": f"{layer}_{path.stem}",
                        "scale": md["res_scale"],
                        "colormap": cmap,
                        "blending": "additive",
                        "metadata": md,
                        "contrast_limits": [0, md["int_scale"]],
                    },
                    "image",
                )
            )

    return img_layer_data


def read_img(img, load_mem):
    """
    Reads an image from a given pathlib path and processes it.

    Parameters:
    img (pathlib.Path): The path to the image file.
    load_mem (bool): Flag to determine if the image should be loaded into memory.

    Returns:
    tuple: A tuple containing:
        - zarray (list): A list of zarr arrays representing the image data.
        - int_scale (int): The intensity scale of the image based on its bit depth.
        - modality (str): The modality of the image, either "BF" (Bright Field) or "IF" (Immunofluorescence).

    Raises:
    NotImplementedError: If the image bit depth is not supported.
    """

    # Loading Image data
    store = tifffile.imread(img, aszarr=True)
    image = zarr.open(store, mode="r")
    if isinstance(image, zarr.hierarchy.Group):
        zarray = [array for _, array in image.arrays()]
    else:
        zarray = [image]
    print(len(zarray), zarray[0], zarray[0].shape)
    dask_array = darray.from_zarr(
        zarray[-1]
    )  # Convert zarr array to Dask array
    max_val, mean_val = darray.compute(dask_array.max(), dask_array.mean())
    # need to add here test for image modality
    print(dask_array.shape, dask_array)
    print(mean_val)
    modality = "BF"
    if mean_val < 100:
        modality = "IF"
    if 1 < max_val <= 255:  # Image in 8bit col
        print("8bit!")
        int_scale = 255
    elif (
        255 < max_val <= 4095
    ):  # Image is 12bit colour, not 16! -> Checking actual values since Bits entry in XML lies and says 12bits for the Luca 8bit image
        print("12bit!")
        int_scale = 4095
        # int_scale = 255
    elif 4095 < max_val <= 65535:  # image in 16bit colour
        print("16 bit!")
        int_scale = 65535
        # int_scale = 255
    else:
        raise NotImplementedError("The image bit depth is not supported.")
    if not load_mem:
        zarray = [darray.from_zarr(array) for array in zarray]
    return zarray, int_scale, modality  # returns list of zarr arrays


def read_md(img, modality):
    """
    Reads metadata from a TIFF image file and returns it as a dictionary.

    Parameters:
    img (str): The file path to the TIFF image.
    modality (str): The imaging modality, e.g., "IF" (Immunofluorescence).

    Returns:
    dict: A dictionary containing the image metadata, including:
        - 'ImagePath': The file path to the image.
        - 'ResolutionUnit': The unit of resolution (e.g., centimeters or inches).
        - 'XResolution': The X resolution of the image.
        - 'YResolution': The Y resolution of the image.
        - 'res_scale': A tuple containing the scaling factors for the X and Y axes.
        - 'path': The file path to the image.
        - 'modality': The imaging modality.
        - 'fluor_to_marker' (if modality is "IF"): A mapping of fluorophores to markers.
        - 'colmap_channels' (if modality is "IF"): Color map channels.
        - 'new_format' (if modality is "IF"): A flag indicating if the new format is used.

    Raises:
    NotImplementedError: If the resolution unit is not in centimeters or inches.
    Warning: If the resolution metadata cannot be detected.
    """
    # Loading Image metadata
    res_scale = (1, 1)
    with tifffile.TiffFile(img) as src:
        full_res_tags = {
            tag.name: tag.value
            for tag in src.series[0].pages[0].tags.values()
            if tag.name
            not in [
                "StripOffsets",
                "StripByteCounts",
                "TileOffsets",
                "TileByteCounts",
            ]
            and not isinstance(tag.value, numpy.ndarray)
        }
        full_res_tags["ImagePath"] = img
        try:
            if str(full_res_tags["ResolutionUnit"]) in [
                "RESUNIT.CENTIMETER",
                "3",
            ]:
                xres = full_res_tags["XResolution"]
                yres = full_res_tags["YResolution"]
                x_scale = xres[1] / xres[0]
                y_scale = yres[1] / yres[0]
                res_scale = (x_scale, y_scale)
            elif str(full_res_tags["ResolutionUnit"]) in ["RESUNIT.INCH", "2"]:
                xres = full_res_tags["XResolution"]
                yres = full_res_tags["YResolution"]
                x_scale = (xres[1] / xres[0]) * 2.54
                y_scale = (yres[1] / yres[0]) * 2.54
                res_scale = (x_scale, y_scale)
            else:
                print(str(full_res_tags["ResolutionUnit"]))
                raise NotImplementedError(
                    "Scaling supports only images in centimeters or inches"
                )
        except Exception as e:
            warning_noMD = warnings.warn(
                f"Could not detect resolution metadata for image \n {img.stem}. \n Exception: {e}"
            )
            WarningNotification(warning_noMD)
        md = full_res_tags
        md["path"] = img
        md["modality"] = modality
        md["res_scale"] = res_scale
        if modality == "IF":
            fluor_to_marker, colmap_channels, new_format = _get_mdIF(src)
            md["fluor_to_marker"] = fluor_to_marker
            md["colmap_channels"] = colmap_channels
            md["new_format"] = new_format
    return md


def _get_mdIF(TiffFile):
    """
    Extract metadata and color mapping from a TIFF file.

    Args:
        TiffFile (TiffFile): An instance of a TIFF file object from which metadata
            and color mapping will be extracted.

    Returns:
        tuple: A tuple containing:
            - fluor_to_marker (dict or bool): A dictionary mapping fluorophores
                to markers if the new format is detected, otherwise False.
            - colmap_channels (dict): A dictionary mapping channel names to their
                respective RGB color tuples.
            - new_format (bool): A boolean indicating whether the new format was detected.
    """
    new_format = False
    single_page_md = False
    fluor_to_marker = False
    xml = ElementTree.fromstring(
        TiffFile.series[0].pages[0].tags["ImageDescription"].value
    )
    if xml.find(".//LibraryAsJSON") is not None:
        import json

        dicti = json.loads(xml.find(".//LibraryAsJSON").text)
        if "spectra" in dicti.keys():
            new_format = True
            fluor_to_marker = {
                item["fluor"]: item["marker"]
                for item in dicti["spectra"]
                if "fluor" in item and "marker" in item
            }
    colmap_channels = {}
    for page in TiffFile.series[0].pages:
        try:
            xml = ElementTree.fromstring(page.tags["ImageDescription"].value)
            if new_format == True:
                colmap_channels[xml.find(".//Responsivity/Band/Name").text] = (
                    tuple(
                        float(x) for x in xml.find(".//Color").text.split(",")
                    )
                )
            else:
                colmap_channels[
                    xml.find(".//Responsivity/Filter/Name").text
                ] = tuple(
                    float(x) for x in xml.find(".//Color").text.split(",")
                )
        except:  # attribute error on the else above and keyerror on the imagedescription
            single_page_md = True
    # EXPERIMENTAL, to be worked upon
    if single_page_md:
        tree = ElementTree.ElementTree(xml)
        filename = f"page_{str(page)}_xml.xml"
        tree.write(filename, encoding="utf-8", xml_declaration=True)
        channels = xml.find(".//channels")
        for channel in channels.findall("channel"):
            channel_id = channel.get("id")
            channel_name = channel.get("name")
            print(channel_name)
            rgb_value = int(channel.get("rgb"))
            # Convert the RGB integer to a tuple of (R, G, B)
            r = (rgb_value >> 16) & 0xFF
            g = (rgb_value >> 8) & 0xFF
            b = rgb_value & 0xFF
            colmap_channels[channel_name] = (r, g, b)
        print(channels)
        print(channels.text)
        print(channels.text.split(","))
    print(colmap_channels)
    colmap_channels = {
        key: tuple(
            v / 255 if max(colmap_channels[key]) > 1 else v for v in val
        )
        for key, val in colmap_channels.items()
    }
    print(colmap_channels)
    return fluor_to_marker, colmap_channels, new_format
