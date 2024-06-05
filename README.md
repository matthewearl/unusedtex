# Quake unused texture hider

This tool blacks out parts of textures that are not used in a map.  For large
trimsheets where only a small portion is used this can lead to a significant
space saving after compression.

This is a proof-of-concept, but the size figures here should be close to what a
more polished version would show.

Here is a before/after comparison on the BSP files from the
[brutalist jam](https://www.slipseer.com/index.php?resources/quake-brutalist-jam.126/):


|                        | uncomp     | comp       | comp w/ tool   | ratio        |
|:-----------------------|:-----------|:-----------|:---------------|:-------------|
| `qbj_Mr_M.bsp`         | 10.976 MB  | 4.494 MB   | 3.259 MB       | 72.512 %     |
| `qbj_annihilator.bsp`  | 28.583 MB  | 11.449 MB  | 9.237 MB       | 80.679 %     |
| `qbj_bmfbr.bsp`        | 51.445 MB  | 9.772 MB   | 8.334 MB       | 85.283 %     |
| `qbj_bonn.bsp`         | 11.820 MB  | 4.871 MB   | 3.743 MB       | 76.841 %     |
| `qbj_chocohearts.bsp`  | 16.614 MB  | 7.499 MB   | 4.157 MB       | 55.427 %     |
| `qbj_chrisholden.bsp`  | 15.914 MB  | 5.443 MB   | 3.760 MB       | 69.067 %     |
| `qbj_chrisholden2.bsp` | 4.659 MB   | 1.805 MB   | 1.159 MB       | 64.216 %     |
| `qbj_colossus.bsp`     | 32.110 MB  | 12.304 MB  | 8.844 MB       | 71.874 %     |
| `qbj_eduardo.bsp`      | 6.125 MB   | 2.259 MB   | 1.755 MB       | 77.688 %     |
| `qbj_ekhudson.bsp`     | 45.066 MB  | 16.795 MB  | 10.935 MB      | 65.111 %     |
| `qbj_fifthskip.bsp`    | 27.932 MB  | 9.964 MB   | 6.912 MB       | 69.363 %     |
| `qbj_grash.bsp`        | 11.237 MB  | 4.719 MB   | 3.761 MB       | 79.697 %     |
| `qbj_greenwood.bsp`    | 4.322 MB   | 1.742 MB   | 1.735 MB       | 99.647 %     |
| `qbj_grue.bsp`         | 17.987 MB  | 6.341 MB   | 6.053 MB       | 95.453 %     |
| `qbj_hcm.bsp`          | 23.335 MB  | 8.496 MB   | 8.468 MB       | 99.669 %     |
| `qbj_hrnekbezucha.bsp` | 18.538 MB  | 7.379 MB   | 6.207 MB       | 84.111 %     |
| `qbj_iyago.bsp`        | 11.334 MB  | 4.568 MB   | 3.207 MB       | 70.204 %     |
| `qbj_magnetbox.bsp`    | 14.576 MB  | 6.460 MB   | 5.089 MB       | 78.789 %     |
| `qbj_mrtaufner.bsp`    | 18.289 MB  | 8.404 MB   | 5.860 MB       | 69.721 %     |
| `qbj_naitelveni.bsp`   | 16.791 MB  | 6.258 MB   | 5.079 MB       | 81.173 %     |
| `qbj_newhouse.bsp`     | 14.810 MB  | 4.560 MB   | 4.321 MB       | 94.759 %     |
| `qbj_pinchy.bsp`       | 13.261 MB  | 4.987 MB   | 3.937 MB       | 78.949 %     |
| `qbj_porglezomp.bsp`   | 15.498 MB  | 5.850 MB   | 2.952 MB       | 50.471 %     |
| `qbj_qalten.bsp`       | 8.622 MB   | 2.704 MB   | 1.762 MB       | 65.176 %     |
| `qbj_rabbit7250.bsp`   | 47.997 MB  | 18.353 MB  | 12.806 MB      | 69.775 %     |
| `qbj_radiatoryang.bsp` | 8.448 MB   | 3.546 MB   | 3.023 MB       | 85.250 %     |
| `qbj_riktoi.bsp`       | 23.416 MB  | 9.828 MB   | 7.135 MB       | 72.594 %     |
| `qbj_sewerh.bsp`       | 41.890 MB  | 16.049 MB  | 8.377 MB       | 52.197 %     |
| `qbj_stickflip.bsp`    | 10.934 MB  | 3.274 MB   | 2.588 MB       | 79.048 %     |
| `qbj_stixc.bsp`        | 14.163 MB  | 5.560 MB   | 3.651 MB       | 65.664 %     |
| `qbj_strideh.bsp`      | 21.898 MB  | 8.105 MB   | 6.320 MB       | 77.970 %     |
| `qbj_tei.bsp`          | 1.492 MB   | 0.498 MB   | 0.480 MB       | 96.338 %     |
| `qbj_unijorse.bsp`     | 9.675 MB   | 3.676 MB   | 2.360 MB       | 64.195 %     |
| `qbj_wiedo.bsp`        | 15.663 MB  | 5.935 MB   | 4.018 MB       | 67.691 %     |
| `qbj_zbidou72.bsp`     | 47.478 MB  | 19.229 MB  | 14.111 MB      | 73.384 %     |
| `start.bsp`            | 18.134 MB  | 6.663 MB   | 5.088 MB       | 76.360 %     |
| *TOTAL*                | 701.033 MB | 259.842 MB | 190.482 MB     | 73.307 %     |


Key:
- uncomp:   The size of the uncompressed BSP file.  This size is the same
  regardless of whether this tool has been used or not
- comp:  The size after the original BSP has been compressed.
- comp w/ tool:  The size after the modified BSP has been compressed.
- ratio:  Size of the compress modified BSP relative to the compressed original
  BSP.

This is after compressing with `zip -9`.  Also note this is considering only BSP
files --- there are other large files in the original QBJ zip which would make
the above ratio less impressive.

## Usage

Make a virtualenv, and run `pip install -r requirements.txt`, then run
`unusedtex.py`:

```bash
python unusedtex.py input.bsp output.bsp
```

## Bugs / limitations

- This only changes the level 0 mip map.  It shouldn't be hard to make it change
  all the mip maps although I doubt it'll make a huge difference.
- Some engines make their own mipmaps using the full size texture rather than
  using the stored mip maps.  I've attempted to be conservative with the mask
  for this reason,  on the assumption that the minimum mip size is 8x8 times as
  small as the full texture.  However I still occasionally see bleeding around
  edges in the distance, so perhaps there are smaller mip maps being generated?
  Needs more work to investigate.
- The masking is done based on 2D texture coordinate bounding boxes.  A bit more
  space saving could be had if the mask accurately rasterizes out the shape of
  the face in TC space.
- Possibly more?  I haven't tested this a lot.
