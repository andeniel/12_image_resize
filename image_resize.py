import argparse
import sys
from PIL import Image
from os.path import basename, splitext, dirname, abspath, join


class ImageSaveException(Exception):

    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


class ImageGeneralException(Exception):

    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


class ImageResizeException(Exception):

    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


class Resize_Image(object):

    def __init__(self, src_path):
        self.src_path = src_path
        self.src_image = Image.open(src_path)
        self.src_format = self.src_image.format

    def smart_resize(self, width, height):
        src_width, src_height = self.src_image.size
        is_landscape = bool(src_width >= src_height)

        if height is None:
            height = int(width * src_height / src_width)
        elif width is None:
            width = int(height * src_width / src_height)
        else:
            if is_landscape is not (width >= height):
                raise ImageGeneralException(
                    "Ориентация исходного изображения "
                    "и нового не соответствует"
                    )
        try:
            self.src_image = self.src_image.resize((width, height))
            return self.src_image
        except IOError:
            raise ImageResizeException("Ошибка в процессе resize")

    def scale(self, scale):
        width, height = self.src_image.size
        new_width = int(width*scale)
        new_height = int(height*scale)
        try:
            self.src_image = self.src_image.resize((new_width, new_height))
            return self.src_image
        except IOError:
            raise ImageResizeException("Ошибка в процессе resize")

    def get_new_filename(self):
        width, height = self.src_image.size
        filename = splitext(basename(self.src_path))
        return join(
                dirname(abspath(self.src_path)),
                "%s__%sx%s%s"
                % (filename[0], width, height, filename[1]))

    def save(self, dest_image):
        dest_image = dest_image if dest_image else self.get_new_filename()
        try:
            self.src_image.save(dest_image, self.src_format)
            return dest_image
        except IOError:
            raise ImageSaveException(
                "Ошибка! Изображение %s не сохранено" % (self.src_path))


def init_arguments():
    aparser = argparse.ArgumentParser()
    aparser.add_argument(
        'source_image',
        help="Source image to resize"
    )
    aparser.add_argument(
        '-W', '--width',
        type=int,
        help="Crop image to Width"
    )
    aparser.add_argument(
        '-H', '--height',
        type=int,
        help="Crop image to Height"
    )
    aparser.add_argument(
        '-s', '--scale',
        type=float,
        help="Scale image"
    )
    aparser.add_argument(
        '-o', '--output',
        help="Output result image to filepath"
    )
    args = aparser.parse_args()
    if args.width is None and args.height is None and args.scale is None:
        return None

    if args.scale and (args.width is not None or args.height is not None):
        return None

    return args


if __name__ == '__main__':
    args = init_arguments()
    if args is None:
        print(
            "Ошибка! необходим хоть один из "
            "аргументов --scale, --width, --height и "
            "не указывать аргумент --scale вместе с "
            "аргументами --width, --height"
        )
        sys.exit(1)

    new_image = Resize_Image(args.source_image)

    try:
        if args.scale:
            new_image.scale(args.scale)
        else:
            new_image.smart_resize(args.width, args.height)

        dest_image = new_image.save(args.output)
        print(
            "Изображение %s успешно сохранено в %s"
            % (args.source_image, dest_image))

    except (
            ImageResizeException,
            ImageGeneralException,
            ImageSaveException) as exception:
        print(exception)
