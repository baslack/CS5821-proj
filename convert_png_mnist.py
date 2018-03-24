import os
import sys

from PIL import Image, ImageChops

kDEBUG = False

if __name__ == "__main__":
    # setup a master byte array and count
    count = 0
    mnist_bytes = bytearray()
    mnist_labels = bytearray()
    # get the file list from the supplied directory
    try:
        filepath = sys.argv[1]
    except IndexError as e:
        print(e, file=sys.stderr)
        exit(-1)
    filepath = os.path.abspath(os.path.expanduser(filepath))
    if kDEBUG:
        print(filepath)
    if os.path.exists(filepath):
        filelist = os.listdir(filepath)
        # filter the list for PNG files
        filelist = filter(lambda x: (x.endswith(".png") or x.endswith(".PNG")), filelist)
    else:
        print("{0} is invalid filepath\r\n".format(filepath), file=sys.stderr)
        exit(-1)
    # with the filtered list
    for this_file in filelist:
        if kDEBUG:
            print("Processing {0}\r\n".format(this_file))
        # open each file

        with Image.open(os.path.join(filepath, this_file)) as f:
            # confirm that the file is
            # greyscale
            if f.mode != "L":
                break
            # 28 x 28
            if f.size != (28, 28):
                break
            # recenter to bounding box
            bb = f.getbbox()
            offset_x = (28 - (bb[2] - bb[0])) // 2 - bb[0]
            offset_y = (28 - (bb[3] - bb[1])) // 2 - bb[1]
            f = ImageChops.offset(f, offset_x, offset_y)
            bb = f.getbbox()
            # if so
            # increment the count
            count += 1
            # add the image content to the master byte array
            mnist_bytes += f.tobytes()

            # parse filename for label
            label = int(this_file.rsplit(".")[0].rsplit("_")[1])
            mnist_labels += label.to_bytes(1, "big")

    # when done with the files
    # open a mnist file
    try:
        filename = sys.argv[2]
    except IndexError as e:
        print(e, file=sys.stderr)
        exit(-1)
    with open(filename, "wb") as f:
        if kDEBUG:
            print("Writing MNIST file: {0}".format(filename))
        # write the magic number (2049 for image data)
        # noinspection PyRedundantParentheses
        f.write((2051).to_bytes(4, "big"))
        # write the count
        f.write(int(count).to_bytes(4, "big"))
        # write the image size x and y
        # noinspection PyRedundantParentheses
        f.write((28).to_bytes(4, "big"))
        # noinspection PyRedundantParentheses
        f.write((28).to_bytes(4, "big"))
        # write the byte array
        f.write(mnist_bytes)

    with open(filename+"_labels", "wb") as f:
        if kDEBUG:
            print("Writing MNIST label file: {0}".format(filename+"_labels"))
        f.write((2049).to_bytes(4, "big"))
        f.write(int(count).to_bytes(4, "big"))
        f.write(mnist_labels)
