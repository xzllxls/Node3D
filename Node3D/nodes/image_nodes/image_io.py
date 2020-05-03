from Node3D.base.node import ImageNode
import cv2
import os
import numpy as np
import OpenImageIO as oiio
imports = ['exr', 'png', 'jpg', 'jpeg', 'tif', 'tiff', 'tga',
           'jp2', 'bmp', 'dib', 'jpe', 'pbm', 'ppm', 'pgm',
           'sr', 'ras', 'hdr']


def get_type(names):
    if len(names) > 1:
        for i in names:
            if i.lower().endswith('.r'):
                return "RGB"
            elif i.lower().endswith('.x'):
                return "XYZ"
            elif i.lower().endswith('.u'):
                return 'UVW'
            elif i.lower().endswith('r'):
                return "RGB"
            elif i.lower().endswith('x'):
                return "XYZ"
            elif i.lower().endswith('u'):
                return 'UVW'
    else:
        return "G"

    return None


def sort_channels(name, mode):
    if mode == "RGB":
        img = [None for _ in range(len(name))]
        for i, n in enumerate(name.copy()):
            if n.lower().endswith("r"):
                img[0] = n
                name.remove(n)
            elif n.lower().endswith("g"):
                img[1] = n
                name.remove(n)
            elif n.lower().endswith("b"):
                img[2] = n
                name.remove(n)
            elif n.lower().endswith("a"):
                img[3] = n
                name.remove(n)
        if None in img:
            for i in name:
                img[img.index(None)] = i
        return img

    elif mode == "XYZ":
        img = [None for _ in range(len(name))]
        for i, n in enumerate(name.copy()):
            if n.lower().endswith("x"):
                img[0] = n
                name.remove(n)
            elif n.lower().endswith("y"):
                img[1] = n
                name.remove(n)
            elif n.lower().endswith("z"):
                img[2] = n
                name.remove(n)
            elif n.lower().endswith("w"):
                img[3] = n
                name.remove(n)
        if None in img:
            for i in name:
                img[img.index(None)] = i
        return img

    elif mode == "UVW":
        # print(name)
        img = [None for _ in range(len(name))]
        for i, n in enumerate(name.copy()):
            if n.lower().endswith("u"):
                img[0] = n
                name.remove(n)
            elif n.lower().endswith("v"):
                img[1] = n
                name.remove(n)
            elif n.lower().endswith("w"):
                img[2] = n
                name.remove(n)
            elif n.lower().endswith("a"):
                img[2] = n
                name.remove(n)

        if None in img:
            for i in name:
                img[img.index(None)] = i
        return img

    elif mode == "G":
        return name


def get_all_channels(image):
    image_data = {}
    image_offset = {}
    _last_name = None
    channel_names = image.spec().channelnames
    real_data = image.read_image()

    for i, name in enumerate(channel_names):
        image_offset[name] = i
        if "." in name:
            n = ".".join(name.split(".")[:-1])
            if n == _last_name:
                image_data[n].append(name)
            else:
                image_data[n] = [name]
            _last_name = n
        else:
            if name.lower() in "rgba":
                has = True
                if 'rgb' in image_data:
                    channel_name = 'rgb'
                elif 'rgba' in image_data:
                    channel_name = 'rgba'
                else:
                    has = False
                    channel_name = 'rgb'
                    for n in channel_names:
                        if n.lower() == 'a':
                            channel_name = 'rgba'
                            break
                if has:
                    image_data[channel_name].append(name)
                else:
                    image_data[channel_name] = [name]
            # elif name.lower() in "xyzw":
            #     has = True
            #     if 'xyz' in image_data:
            #         channel_name = 'xyz'
            #     elif 'xyzw' in image_data:
            #         channel_name = 'xyzw'
            #     else:
            #         has = False
            #         channel_name = 'xyz'
            #         for n in channel_names:
            #             if n.lower() == 'w':
            #                 channel_name = 'xyzw'
            #                 break
            #     if has:
            #         image_data[channel_name].append(name)
            #     else:
            #         image_data[channel_name] = [name]
            else:
                image_data[name] = [name]

    np_image_data = {}

    for name, n in image_data.items():
        channel_type = get_type(n)
        if channel_type is None:
            print("*" * 10)
        channels = sort_channels(n, channel_type)

        if channels is None:
            print("************* can not merge", name, n, channel_type)
            continue
        if None in channels:
            print("************* has None", name, n, channel_type, channels)
            continue

        indices = [image_offset[channel_name] for channel_name in channels]
        try:
            if len(indices) == 0:
                d = real_data[indices[0]]
                if len(d.shape) == 3:
                    d = d.reshape((d.shape[0], d.shape[1]))
                np_image_data[name] = d.transpose((1, 0))
            else:
                np_image_data[name] = real_data[..., indices].transpose((1, 0, 2))
        except Exception as e:
            print(e)
            print("************* can not convert ", name, n, channel_type, indices)

    return np_image_data


class File(ImageNode):
    # set a unique node identifier.
    __identifier__ = 'IO'

    # set the initial default node name.
    NODE_NAME = 'File Import'

    def __init__(self):
        super(File, self).__init__()
        ext = "*." + ";*.".join(imports)
        self.add_file_input("file", "file", ext=ext)

    def run(self):
        self.image = None
        file_path = self.get_property('file')
        if not os.path.exists(file_path):
            return

        # opencv
        # self.image = cv2.imread(file_path, cv2.IMREAD_UNCHANGED)
        # if "int" in self.image.dtype.name:
        #     self.image = self.image.astype(np.float32) / float(np.iinfo(self.image.dtype).max)
        # self.image = self.image.transpose((1, 0, 2))
        # self.image[..., [0, 1, 2]] = self.image[..., [2, 1, 0]]

        # oiio
        image = oiio.ImageInput.open(file_path)
        self.image = get_all_channels(image)


class Render(ImageNode):
    # set a unique node identifier.
    __identifier__ = 'IO'

    # set the initial default node name.
    NODE_NAME = 'Render Output'

    def __init__(self):
        super(Render, self).__init__()
        ext = "*." + ";*.".join(imports)
        self.add_file_input("file", "file", ext=ext)
