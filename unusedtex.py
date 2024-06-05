import logging
import struct
import sys

import numpy as np
import tqdm

import pyquake.bsp


logger = logging.getLogger(__name__)


def _mark_bbox(face, mip_level):
    assert mip_level == 0
    tex = face.tex_info.texture
    tex_size = tex.width, tex.height

    tcs = np.array(face.tex_coords)

    mins = np.floor(np.min(tcs/8 - 1e-3, axis=0)).astype(int) * 8
    maxs = np.ceil(np.max(tcs/8 + 1e-3, axis=0)).astype(int) * 8

    tile_start = mins // tex_size
    tile_end = ((maxs - 1) // tex_size) + 1

    marked = np.zeros((tex.height, tex.width), dtype=bool)
    for tile_y in range(tile_start[1], tile_end[1]):
        for tile_x in range(tile_start[0], tile_end[0]):
            tile = np.array([tile_x, tile_y])
            tiled_mins = np.maximum(mins - tile * tex_size, 0)
            tiled_maxs = np.minimum(maxs - tile * tex_size, tex_size)

            marked[
                tiled_mins[1]:tiled_maxs[1],
                tiled_mins[0]:tiled_maxs[0]
            ] = True

    return marked


def _read_struct(f, struct_fmt):
    size = struct.calcsize(struct_fmt)
    out = struct.unpack(struct_fmt, f.read(size))
    return out


def _read_dir_entry(f, idx):
    fmt = "<II"
    size = struct.calcsize(fmt)
    f.seek(4 + size * idx)
    return struct.unpack(fmt, f.read(size))


def _get_texture_data_offsets(f):
    de_offset, size = _read_dir_entry(f, 2)

    f.seek(de_offset)
    num_textures, = _read_struct(f, "<L")
    tex_offsets = [_read_struct(f, "<l")[0] for i in range(num_textures)]
    tex_offsets = [de_offset + offs for offs in tex_offsets if offs != -1]

    for tex_offset in tex_offsets:
        f.seek(tex_offset)
        name, width, height, *data_offsets = _read_struct(f, "<16sLL4l")
        name = name[:name.index(b'\0')].decode('ascii')

        offset = 40
        for i in range(4):
            if data_offsets[i] != -1:
                if offset != data_offsets[i]:
                    raise Exception('Data offset is {} expected {}'.format(
                        data_offsets[i], offset)
                    )
                mip_size = (width * height) >> (2 * i)

                start = f.tell()
                yield (name, i), (start, mip_size)
                f.seek(start + mip_size)
                offset += mip_size


def _mark_all(b):
    all_marked = {}
    for face in tqdm.tqdm(b.faces):
        mip_level = 0

        if face.tex_info.texture_exists:
            tex_name = face.tex_info.texture.name
            if (not tex_name.startswith('sky')
                    and not tex_name.startswith('*')
                    and face.tex_info.texture.data[mip_level] is not None):
                marked = _mark_bbox(face, mip_level)
                if (tex_name, mip_level) not in all_marked:
                    all_marked[tex_name, mip_level] = np.zeros_like(marked)
                all_marked[tex_name, mip_level] |= marked

    return all_marked


def remove_unused_textures(in_fname, out_fname):
    logger.info('reading map')
    with open(in_fname, 'rb') as f:
        b = pyquake.bsp.Bsp(f)

    logger.info('marking all faces')
    all_marked = _mark_all(b)

    logger.info('writing file')
    with open(in_fname, 'rb') as f:
        tex_offsets = dict(_get_texture_data_offsets(f))

    with open(in_fname, 'rb') as f:
        map_arr = np.frombuffer(f.read(), dtype=np.uint8).copy()

    for (tex_name, mip_index), marked in tqdm.tqdm(all_marked.items()):
        offset, size = tex_offsets[tex_name, mip_index]
        assert (
            map_arr[offset:offset+size].tobytes()
            == b.textures_by_name[tex_name].data[mip_index]
        )
        map_arr[offset:offset+size] = np.where(
            marked.ravel(),
            map_arr[offset:offset+size],
            251    # Change to zero to make any bleeding less obvious.
        )

    with open(out_fname, 'wb') as f:
        f.write(map_arr.tobytes())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    in_fname, out_fname = sys.argv[1:3]
    remove_unused_textures(in_fname, out_fname)
