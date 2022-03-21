import numpy as np
import cv2
from PIL import Image


def strip_manga(folder, numPage):
    strips_total = []
    # Iteration over the pages of the chapter
    for j in range(1, numPage + 1):
        # List of the sections for each strips
        strips = [[], [], []]
        # Read page
        print("folder: ", folder)
        src = cv2.imread(f"manga/{folder}/{j}.jpg")
        # cv2.imshow('img', src)
        height, width, chn = src.shape
        seed = (0, 0)
        src = cv2.erode(src, np.ones((2, 2), np.uint8), iterations=1)
        mask = np.zeros((height + 2, width + 2), np.uint8)

        floodflags = 4
        floodflags |= cv2.FLOODFILL_MASK_ONLY
        floodflags |= 255 << 8

        threshold = 10

        num, im, floodfilled, rect = cv2.floodFill(
            src,
            mask,
            (0, 0),
            (255, 0, 0),
            (threshold,) * 3,
            (threshold,) * 3,
            floodflags,
        )
        num, im, floodfilled, rect = cv2.floodFill(
            src,
            mask,
            (0, height - 2),
            (255, 0, 0),
            (threshold,) * 3,
            (threshold,) * 3,
            floodflags,
        )
        num, im, floodfilled, rect = cv2.floodFill(
            src,
            mask,
            (width - 2, 0),
            (255, 0, 0),
            (threshold,) * 3,
            (threshold,) * 3,
            floodflags,
        )
        num, im, floodfilled, rect = cv2.floodFill(
            src,
            mask,
            (width - 2, height - 2),
            (255, 0, 0),
            (threshold,) * 3,
            (threshold,) * 3,
            floodflags,
        )
        whiteArea = cv2.countNonZero(floodfilled)
        print(whiteArea)

        # cv2.imshow('floodfilled', floodfilled)

        contours, _ = cv2.findContours(
            floodfilled, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
        )

        i = 0

        contours_big = [cont for cont in contours if cv2.contourArea(cont) > 2000]
        # list for storing names of shapes
        for contour in contours_big:
            # here we are ignoring first counter because
            # findcontour function detects whole image as shape
            if i == 0:
                i = 1
                continue

            # cv2.approxPloyDP() function to approximate the shape
            approx = cv2.approxPolyDP(
                contour, 0.01 * cv2.arcLength(contour, True), True
            )

            # using drawContours() function
            # cv2.drawContours(src, [contour], 0, (0, 0, 255), 5)

            # finding center point of shape
            M = cv2.moments(contour)
            if M["m00"] != 0.0:

                x = int(M["m10"] / M["m00"])
                y = int(M["m01"] / M["m00"])
                # cv2.putText(
                #     src,
                #     f"({x}, {y})",
                #     (x, y + 20),
                #     cv2.FONT_HERSHEY_SIMPLEX,
                #     0.6,
                #     (0, 0, 255),
                #     2,
                # )
                # cv2.line(src, (0, y), (w, y), (0, 255, 0), 2)
                if y <= height / 3:
                    strips[0].append(contour)
                elif y <= height / 3 * 2:
                    strips[1].append(contour)
                else:
                    strips[2].append(contour)

        #     # putting shape name at center of each shape
        #     if len(approx) == 3:
        #         # cv2.putText(
        #         #     src,
        #         #     "Triangle",
        #         #     (x, y),
        #         #     cv2.FONT_HERSHEY_SIMPLEX,
        #         #     0.6,
        #         #     (0, 0, 255),
        #         #     2,
        #         # )
        #
        #     elif len(approx) == 4:
        #         # cv2.putText(
        #         #     src,
        #         #     "Quadrilateral",
        #         #     (x, y),
        #         #     cv2.FONT_HERSHEY_SIMPLEX,
        #         #     0.6,
        #         #     (0, 0, 255),
        #         #     2,
        #         # )
        #
        #     elif len(approx) == 5:
        #         # cv2.putText(
        #         #     src,
        #         #     "Pentagon",
        #         #     (x, y),
        #         #     cv2.FONT_HERSHEY_SIMPLEX,
        #         #     0.6,
        #         #     (0, 0, 255),
        #         #     2,
        #         # )
        #
        #     elif len(approx) == 6:
        #         # cv2.putText(
        #         #     src,
        #         #     "Hexagon",
        #         #     (x, y),
        #         #     cv2.FONT_HERSHEY_SIMPLEX,
        #         #     0.6,
        #         #     (0, 0, 255),
        #         #     2,
        #         # )
        #
        #     else:
        #         cv2.putText(
        #             src, "circle", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2
        #         )
        # # cv2.imshow('img', src)

        im = Image.fromarray(src)
        if len(strips[0]) > 0:
            for cont in strips[0]:
                x, y, w, h = cv2.boundingRect(cont)
                cv2.rectangle(src, (x, y), (x + w, y + h), (255, 255, 0), 2)
                cv2.fillPoly(src, pts=[cont], color=(255, 0, 0))
            maxCutFirst = (
                cv2.boundingRect(
                    max(
                        strips[0],
                        key=lambda con: cv2.boundingRect(con)[1]
                        + cv2.boundingRect(con)[3],
                    )
                )[1]
                + cv2.boundingRect(
                    max(
                        strips[0],
                        key=lambda con: cv2.boundingRect(con)[1]
                        + cv2.boundingRect(con)[3],
                    )
                )[3]
            )
            minCutFirst = cv2.boundingRect(
                min(strips[0], key=lambda con: cv2.boundingRect(con)[1])
            )[1]
            firstStrip = im.crop((0, minCutFirst, width - 1, maxCutFirst))

            widthStrip, heightStrip = firstStrip.size
            oldSize = firstStrip.size
            if widthStrip / heightStrip > 4 / 3:
                newSize = (widthStrip, int(widthStrip * 3 / 4))
            else:
                newSize = (int(heightStrip * 4 / 3), heightStrip)
            firstStrip = firstStrip.convert("RGB")
            centeredIm = Image.new("RGB", newSize, (255, 255, 255))
            centeredIm.paste(
                firstStrip,
                ((newSize[0] - oldSize[0]) // 2, (newSize[1] - oldSize[1]) // 2),
            )
            strips_total.append(centeredIm)
            centeredIm.save(f"manga/{folder}/{j}first.jpg")
        if len(strips[1]) > 0:
            for cont in strips[1]:
                x, y, w, h = cv2.boundingRect(cont)
                cv2.rectangle(src, (x, y), (x + w, y + h), (0, 255, 255), 2)
                cv2.fillPoly(src, pts=[cont], color=(0, 255, 0))
            maxCutSecond = (
                cv2.boundingRect(
                    max(
                        strips[1],
                        key=lambda con: cv2.boundingRect(con)[1]
                        + cv2.boundingRect(con)[3],
                    )
                )[1]
                + cv2.boundingRect(
                    max(
                        strips[1],
                        key=lambda con: cv2.boundingRect(con)[1]
                        + cv2.boundingRect(con)[3],
                    )
                )[3]
            )
            minCutSecond = cv2.boundingRect(
                min(strips[1], key=lambda con: cv2.boundingRect(con)[1])
            )[1]
            secondStrip = im.crop((0, minCutSecond, width - 1, maxCutSecond))
            widthStrip, heightStrip = secondStrip.size
            oldSize = secondStrip.size
            if widthStrip / heightStrip > 4 / 3:
                newSize = (widthStrip, int(widthStrip * 3 / 4))
            else:
                newSize = (int(heightStrip * 4 / 3), heightStrip)
            secondStrip = secondStrip.convert("RGB")
            centeredIm = Image.new("RGB", newSize, (255, 255, 255))
            centeredIm.paste(
                secondStrip,
                ((newSize[0] - oldSize[0]) // 2, (newSize[1] - oldSize[1]) // 2),
            )
            strips_total.append(centeredIm)
            centeredIm.save(f"manga/{folder}/{j}second.jpg")
        if len(strips[2]) > 0:
            for cont in strips[2]:
                x, y, w, h = cv2.boundingRect(cont)
                cv2.rectangle(src, (x, y), (x + w, y + h), (255, 0, 255), 2)
                cv2.fillPoly(src, pts=[cont], color=(0, 0, 255))
            maxCutThird = (
                cv2.boundingRect(
                    max(
                        strips[2],
                        key=lambda con: cv2.boundingRect(con)[1]
                        + cv2.boundingRect(con)[3],
                    )
                )[1]
                + cv2.boundingRect(
                    max(
                        strips[2],
                        key=lambda con: cv2.boundingRect(con)[1]
                        + cv2.boundingRect(con)[3],
                    )
                )[3]
            )
            minCutThird = cv2.boundingRect(
                min(strips[2], key=lambda con: cv2.boundingRect(con)[1])
            )[1]
            thirdStrip = im.crop((0, minCutThird, width - 1, maxCutThird))
            widthStrip, heightStrip = thirdStrip.size
            oldSize = thirdStrip.size
            if widthStrip / heightStrip > 4 / 3:
                newSize = (widthStrip, int(widthStrip * 3 / 4))
            else:
                newSize = (int(heightStrip * 4 / 3), heightStrip)
            thirdStrip = thirdStrip.convert("RGB")
            centeredIm = Image.new("RGB", newSize, (255, 255, 255))
            centeredIm.paste(
                thirdStrip,
                ((newSize[0] - oldSize[0]) // 2, (newSize[1] - oldSize[1]) // 2),
            )
            strips_total.append(centeredIm)
            centeredIm.save(f"manga/{folder}/{j}third.jpg")
        # cv2.imshow('floodfilled', src)
        # cv2.waitKeyEx()
    strips_total[0].save(
        f"manga/{folder}/totalStrips.pdf", save_all=True, append_images=strips_total[1:]
    )


if __name__ == "__main__":
    strip_manga(624, 15)
