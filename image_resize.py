import argparse
from PIL import Image
from os.path import basename, splitext, dirname, abspath, join


class ResizeImage(object):

    def __init__(self, src_path):
        self.src_path = src_path
        self.src_image = Image.open(src_path)
        self.src_format = self.src_image.format

    def smart_resize(self, width, height):
        src_width, src_height = self.src_image.size
        is_landscape = True if src_width >= src_height else False

        if height is None:
            height = int(width * src_height / src_width)
        elif width is None:
            width = int(height * src_width / src_height)
        else:
            if is_landscape is not (width >= height):
                print("Ориентация исходного изображения \
                и нового не соответствует")
                return None
        try:
            self.src_image = self.src_image.resize((width, height))
            return self.src_image
        except IOError:
            return None

    def scale(self, scale):
        width, height = self.src_image.size
        new_width = int(width*scale)
        new_height = int(height*scale)
        try:
            self.src_image = self.src_image.resize((new_width, new_height))
            return self.src_image
        except IOError:
            return None

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
            print(
                "Изображение %s успешно сохранено в %s"
                % (self.src_path, dest_image))
            return dest_image
        except IOError:
            print("Ошибка! Изображение %s не сохранено" % (self.src_path))
            return None

if __name__ == '__main__':
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
    resizeImage = ResizeImage(args.source_image)

    if (args.width or args.height) and args.scale:
        print("Ошибка, параметр scale указывается без ширины или высоты")
        exit(1)
    elif args.scale:
        if resizeImage.scale(args.scale):
            print("Размер изображения успешно изменен!")
            resizeImage.save(args.output)
        else:
            print("Ошибка! Во время операции scale")
    else:
        if args.width or args.height:
            if resizeImage.smart_resize(args.width, args.height):
                print("Размер изображения успешно изменен!")
                resizeImage.save(args.output)
            else:
                print("Ошибка! Во время операции resize")
        else:
            print(
                "Ошибка! необходим хоть один из \
                параметров --scale, --width, --height")
