from sys import argv
from byuimage import Image
#--------------------------------------------------------------
def validate_commands(arguments):
    valid = {"-d":2, "-k":3, "-s":3, "-g":3, "-b":6, "-f":3, "-m":3, "-c":7, "-y":7}
    if arguments[1] in valid:
        if len(arguments) >= valid[arguments[1]]:
            return True
    return False

def darken(infile, outfile, percent):
    per = 1 - float(percent)
    pic = Image(infile)
    newpic = Image.blank(pic.width, pic.height)
    for y in range(pic.height):
        for x in range(pic.width):
            pixel =  pic.get_pixel(x,y)
            n_pixel = newpic.get_pixel(x, y)
            n_pixel.red = pixel.red * per
            n_pixel.green = pixel.green * per
            n_pixel.blue = pixel.blue * per
    newpic.save(outfile)
    return newpic

def sepia(filename, outfile):
    pic = Image(filename)
    for pixel in pic:
        true_red = 0.393 * pixel.red + 0.769 * pixel.green + 0.189 * pixel.blue
        true_green = 0.349 * pixel.red + 0.686 * pixel.green + 0.168 * pixel.blue
        true_blue = 0.272 * pixel.red + 0.534 * pixel.green + 0.131 * pixel.blue
        pixel.green = true_green
        pixel.blue = true_blue
        pixel.red = true_red
        if pixel.red > 255:
            pixel.red = 255
        if pixel.blue > 255:
            pixel.blue = 255
        if pixel.green > 255:
            pixel.green = 255
    pic.save(outfile)
    return pic

def grayscale(filename, outfile):
    pic = Image(filename)
    for pixel in pic:
        average = (pixel.red + pixel.green + pixel.blue) / 3
        pixel.green = average
        pixel.blue = average
        pixel.red = average
    pic.save(outfile)
    return pic

def make_borders(filename, outfile, weight, r,g,b):
    image = Image(filename)
    new_image = Image.blank(image.width + weight*2, image.height + weight*2)
    nw = new_image.width - weight
    nh = new_image.height - weight

    for x in range(new_image.width):
        for y in  range(new_image.height):
            if x < weight or x >= nw or y < weight or y >= nh:
                n_pixel = new_image.get_pixel(x,y)
                n_pixel.red = r
                n_pixel.green = g
                n_pixel.blue = b
            else:
                pixel = image.get_pixel(x - weight,y - weight)
                n_pixel = new_image.get_pixel(x,y)
                n_pixel.red = pixel.red
                n_pixel.green= pixel.green
                n_pixel.blue = pixel.blue
    new_image.save(outfile)
    return new_image

def flipped(filename, outfile):
    image = Image(filename)
    new_image = Image.blank(image.width, image.height)

    for y in range(image.height):
        for x in range(image.width):
            pixel = image.get_pixel(x, y)
            nx = x
            ny = image.height - y - 1
            new_image.get_pixel(nx, ny).color = pixel.color
    new_image.save(outfile)
    return new_image

def mirror(filename, outfile):
    image = Image(filename)
    new_image = Image.blank(image.width, image.height)
    for y in range(image.height):
        for x in range(image.width):
            pixel = image.get_pixel(x, y)
            nx = image.width - x - 1
            ny = y
            new_image.get_pixel(nx, ny).color = pixel.color
    new_image.save(outfile)
    return new_image

def collage(filename, pic1, pic2, pic3, pic4, outfile, thickness):
    image1 = Image(pic1)
    image2 = Image(pic2)
    image3 = Image(pic3)
    image4 = Image(pic4)

    # Assuming all images are of the same size for simplicity
    width = image1.width
    height = image1.height
    collage_width = 2 * width + 3 * thickness
    collage_height = 2 * height + 3 * thickness

    new_image = Image.blank(collage_width, collage_height)

    for y in range(collage_height):
        for x in range(collage_width):
            if x < thickness or x >= collage_width - thickness or y < thickness or y >= collage_height - thickness or \
                    (x >= width + thickness and x < width + 2 * thickness) or \
                    (y >= height + thickness and y < height + 2 * thickness):
                pixel = new_image.get_pixel(x, y)
                pixel.red = 0
                pixel.green = 0
                pixel.blue = 0
            else:
                if x < width + thickness and y < height + thickness:
                    pixel = image1.get_pixel(x - thickness, y - thickness)
                elif x >= width + 2 * thickness and y < height + thickness:
                    pixel = image2.get_pixel(x - (width + 2 * thickness), y - thickness)
                elif x < width + thickness and y >= height + 2 * thickness:
                    pixel = image3.get_pixel(x - thickness, y - (height + 2 * thickness))
                else:
                    pixel = image4.get_pixel(x - (width + 2 * thickness), y - (height + 2 * thickness))
                new_pixel = new_image.get_pixel(x, y)
                new_pixel.red = pixel.red
                new_pixel.green = pixel.green
                new_pixel.blue = pixel.blue

    new_image.save(outfile)
    return new_image


def detectgreen(pixel, threshold):
    return pixel.green >= threshold and pixel.green >= pixel.red and pixel.green >= pixel.blue

def greenscreen(fore, back, outfile, threshold, factor):
    foreground = Image(fore)
    background = Image(back)
    new_image = Image.blank(foreground.width, foreground.height)

    for x in range(foreground.width):
        for y in range(foreground.height):
            fpixel = foreground.get_pixel(x, y)
            bpixel = background.get_pixel(x, y)
            n_pixel = new_image.get_pixel(x, y)

            if detectgreen(fpixel, threshold):
                n_pixel.red = min(255, int(bpixel.red * factor))
                n_pixel.green = min(255, int(bpixel.green * factor))
                n_pixel.blue = min(255, int(bpixel.blue * factor))
            else:
                n_pixel.red = fpixel.red
                n_pixel.green = fpixel.green
                n_pixel.blue = fpixel.blue

    new_image.save(outfile)
    return new_image



#---------------------------------------------------------------
def main(argv):
    if validate_commands(argv) == True:
        flag = argv[1]
        filename = argv[2]

        if flag == "-d":
            p = Image(filename)
            p.show()

        if flag == "-k":
            outfile = argv[3]
            percent = float(argv[4])
            p = darken(filename, outfile, percent)
            p.show()

        if flag == "-s":
            outfile = argv[3]
            p = sepia(filename, outfile)
            p.show()

        if flag == "-g":
            outfile = argv[3]
            p = grayscale(filename, outfile)
            p.show()

        if flag == "-b":
            outfile = argv[3]
            thickness = int(argv[4])
            r = int(argv[5])
            g = int(argv[6])
            b = int(argv[7])
            p = make_borders(filename, outfile, thickness, r, g, b)
            p.show()

        if flag == "-f":
            outfile = argv[3]
            p = flipped(filename, outfile)
            p.show()

        if flag == "-m":
            outfile = argv[3]
            p = mirror(filename, outfile)
            p.show()

        elif flag == "-c":
            pic1 = argv[2]
            pic2 = argv[3]
            pic3 = argv[4]
            pic4 = argv[5]
            outfile = argv[6]
            thickness = int(argv[7])
            p = collage(filename, pic1, pic2, pic3, pic4, outfile, thickness)
            p.show()


        elif flag == "-y":
            fore = argv[2]
            back = argv[3]
            outfile = argv[4]
            threshold = int(argv[5])
            factor = float(argv[6])
            p = greenscreen(fore, back, outfile, threshold, factor)
            p.show()


    else:
        return("Error, the given command is not valid. "
               "Make sure you have the number of inputs for your desired fiter")

if __name__ == "__main__":
    result = main(argv)
    if result:
        print(result)
