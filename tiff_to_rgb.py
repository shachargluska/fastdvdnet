import argparse
import rawpy
from pathlib import Path
from PIL import Image


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filepath', nargs='+')
    parser.add_argument('--root')
    args = parser.parse_args()

    for filepath in args.filepath:
        with rawpy.imread(filepath) as raw:
            # GBGR to RGBG
            assert raw.color_desc == b'RGBG', raw.color_desc
            H, W = raw.raw_image.shape
            raw_image = raw.raw_image.reshape(H//2, W//2, 4)
            raw_image[:, :, :] = raw_image[:, :, [1, 2, 3, 0]]
            raw_image = raw_image.reshape(H, W)
            raw.raw_image[:, :] = raw_image[:, :]

            rgb = raw.postprocess(use_auto_wb=True, user_black=240, user_sat=2**12-1)
            # I think the previous fix causes he result to be in BGR rather than RGB
            rgb = rgb[..., ::-1]

        rgb_image = Image.fromarray(rgb)

        if not args.root:
            name = Path(filepath).with_suffix('.png').name
            rgb_image.save(name)
        else:
            name = Path(filepath).relative_to(args.root).with_suffix('.png')
            name.parent.mkdir(parents=True, exist_ok=True)
            rgb_image.save(name)

