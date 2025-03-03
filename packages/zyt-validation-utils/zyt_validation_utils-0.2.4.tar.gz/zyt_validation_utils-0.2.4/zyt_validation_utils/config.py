# -*- coding: utf-8 -*-
"""
Project Name: zyt_validation_utils
File Created: 2025.01.21
Author: ZhangYuetao
File Name: config.py
Update: 2025.03.03
"""


# 定义支持的图片扩展名
IMAGE_MAP = {
    '.png',  # Portable Network Graphics
    '.jpg',  # JPEG image
    '.jpeg',  # JPEG image
    '.gif',  # Graphics Interchange Format
    '.bmp',  # Bitmap image
    '.webp',  # WebP image
    '.tiff',  # Tagged Image File Format
    '.tif',  # Tagged Image File Format (short form)
    '.svg',  # Scalable Vector Graphics
    '.ico',  # Icon file
    '.heic',  # High Efficiency Image Format (used in iOS)
    '.heif',  # High Efficiency Image Format
    '.psd',  # Adobe Photoshop Document
    '.raw',  # Raw image formats (generic)
    '.cr2',  # Canon Raw 2
    '.nef',  # Nikon Electronic Format
    '.dng',  # Digital Negative
    '.arw',  # Sony Alpha Raw
    '.ppm',  # Portable Pixmap
    '.pgm',  # Portable Graymap
    '.pbm',  # Portable Bitmap
    '.pnm',  # Portable Anymap
    '.hdr',  # High Dynamic Range Image
    '.exr',  # OpenEXR Image
    '.jp2',  # JPEG 2000
    '.j2k',  # JPEG 2000
    '.jpf',  # JPEG 2000
    '.jpx',  # JPEG 2000
    '.jpm',  # JPEG 2000
    '.jxr',  # JPEG XR
    '.wdp',  # Windows Media Photo
    '.dds',  # DirectDraw Surface
    '.xcf',  # GIMP image file
    '.pcx',  # PC Paintbrush Exchange
    '.tga',  # Truevision TGA
    '.raf',  # Fuji RAW
    '.orf',  # Olympus RAW
    '.sr2',  # Sony RAW
    '.rw2',  # Panasonic RAW
    '.pef',  # Pentax RAW
    '.x3f',  # Sigma RAW
    '.3fr',  # Hasselblad RAW
    '.mef',  # Mamiya RAW
    '.erf',  # Epson RAW
    '.kdc',  # Kodak RAW
    '.dcr',  # Kodak RAW
    '.mos',  # Leaf RAW
    '.mrw',  # Minolta RAW
    '.nrw',  # Nikon RAW
    '.ptx',  # Pentax RAW
    '.r3d',  # Redcode RAW
    '.rwl',  # Leica RAW
    '.srw',  # Samsung RAW
    '.bay',  # Casio RAW
}

# 定义支持的视频扩展名
VIDEO_MAP = {
    '.mp4',  # MPEG-4 Part 14
    '.mkv',  # Matroska Video
    '.avi',  # Audio Video Interleave
    '.mov',  # Apple QuickTime Movie
    '.wmv',  # Windows Media Video
    '.flv',  # Flash Video
    '.webm',  # WebM Video
    '.mpeg',  # MPEG Video
    '.mpg',  # MPEG Video (short form)
    '.m4v',  # iTunes Video
    '.3gp',  # 3GPP Multimedia File
    '.3g2',  # 3GPP2 Multimedia File
    '.ogv',  # Ogg Video
    '.vob',  # DVD Video Object
    '.ts',  # MPEG Transport Stream
    '.mts',  # AVCHD Video File
    '.m2ts',  # Blu-ray BDAV Video File
    '.rm',  # RealMedia
    '.rmvb',  # RealMedia Variable Bitrate
    '.asf',  # Advanced Systems Format
    '.divx',  # DivX Video
    '.f4v',  # Flash MP4 Video
    '.mxf',  # Material Exchange Format
    '.ogm',  # Ogg Media
    '.dv',  # Digital Video
    '.dat',  # VCD Video File
    '.mod',  # JVC Everio Video File
    '.tod',  # JVC Everio Video File
    '.trp',  # HD Video Transport Stream
    '.m2v',  # MPEG-2 Video
    '.mpe',  # MPEG Video (short form)
    '.nsv',  # Nullsoft Streaming Video
    '.amv',  # Anime Music Video
    '.svi',  # Samsung Video
    '.k3g',  # KDDI 3GPP Video
    '.drc',  # DiRAC Video
    '.qt',  # QuickTime Video
    '.yuv',  # YUV Video
    '.hevc',  # High Efficiency Video Coding (H.265)
    '.h264',  # H.264 Video
    '.av1',  # AOMedia Video 1
    '.vp9',  # VP9 Video
    '.swf',  # Small Web Format (Flash Video)
    '.rec',  # Recorded Video
    '.arf',  # WebEx Advanced Recording Format
    '.ivf',  # Indeo Video Format
    '.bik',  # Bink Video
    '.xvid',  # Xvid Video
}

# 定义支持的音频扩展名
AUDIO_MAP = {
    '.mp3',  # MPEG Audio Layer III
    '.wav',  # Waveform Audio File Format
    '.aac',  # Advanced Audio Coding
    '.flac',  # Free Lossless Audio Codec
    '.ogg',  # Ogg Vorbis Audio
    '.m4a',  # MPEG-4 Audio
    '.wma',  # Windows Media Audio
    '.aiff',  # Audio Interchange File Format
    '.ape',  # Monkey's Audio
    '.alac',  # Apple Lossless Audio Codec
    '.opus',  # Opus Audio
    '.amr',  # Adaptive Multi-Rate Audio Codec
    '.ac3',  # Dolby Digital Audio
    '.aif',  # Audio Interchange File (short form)
    '.aifc',  # Compressed Audio Interchange File
    '.cda',  # CD Audio Track
    '.mid',  # MIDI Audio
    '.midi',  # MIDI Audio (long form)
    '.mp2',  # MPEG Audio Layer II
    '.mpa',  # MPEG Audio
    '.mpc',  # Musepack Audio
    '.oga',  # Ogg Audio
    '.spx',  # Speex Audio
    '.wv',  # WavPack Audio
    '.ra',  # RealAudio
    '.rm',  # RealMedia Audio
    '.ram',  # RealAudio Metadata
    '.dts',  # DTS Audio
    '.pcm',  # Pulse Code Modulation
    '.adpcm',  # Adaptive Differential Pulse Code Modulation
    '.gsm',  # GSM Audio
    '.mka',  # Matroska Audio
    '.qcp',  # Qualcomm PureVoice
    '.voc',  # Creative Voice File
    '.8svx',  # 8SVX Audio
    '.au',  # Sun Microsystems Audio
    '.snd',  # Sound File
    '.weba',  # WebM Audio
    '.xm',  # FastTracker 2 Audio
    '.mod',  # Module Audio
    '.it',  # Impulse Tracker Audio
    '.s3m',  # ScreamTracker 3 Audio
    '.mtm',  # MultiTracker Module
    '.669',  # Composer 669 Audio
    '.dsm',  # Digital Sound Module
    '.far',  # Farandole Composer Audio
    '.gdm',  # General Digital Music
    '.ult',  # UltraTracker Audio
    '.stm',  # ScreamTracker Audio
    '.med',  # OctaMED Audio
    '.okt',  # Oktalyzer Audio
    '.ptm',  # PolyTracker Module
    '.mdl',  # DigiTrakker Audio
    '.dbm',  # DigiBooster Pro Audio
    '.digi',  # DigiBooster Audio
    '.j2b',  # Jazz Jackrabbit 2 Audio
    '.psm',  # Protracker Studio Module
    '.umx',  # Unreal Music Package
}

# 定义支持的常见压缩文件扩展名
ARCHIVE_MAP = {
    '.zip',  # ZIP Archive
    '.rar',  # RAR Archive
    '.7z',   # 7-Zip Archive
    '.tar',  # Tape Archive
    '.gz',   # Gzip Compressed File
    '.bz2',  # Bzip2 Compressed File
    '.xz',   # XZ Compressed File
    '.tar.gz',  # Gzipped Tar Archive
    '.tar.bz2', # Bzipped Tar Archive
    '.tar.xz',  # XZ Compressed Tar Archive
    '.tgz',     # Gzipped Tar Archive (short form)
    '.tbz2',    # Bzipped Tar Archive (short form)
    '.txz',     # XZ Compressed Tar Archive (short form)
    '.zst',     # Zstandard Compressed File
    '.001',     # Split Archive Part 1 (常见分卷压缩格式)
    '.002',     # Split Archive Part 2
    '.003',     # Split Archive Part 3
}

PIL_RGB_LIST = ['RGB', 'RGBA', 'P', 'CMYK', 'YCbCr', 'LAB', 'HSV', 'RGBa', 'PA', 'RGBX', 'BGR;15', 'BGR;16', 'BGR;24']

PIL_GRAY_LIST = ['1', 'L', 'La', 'LA']

PIL_DEPTH_LIST = ['I', 'F', 'I;16', 'I;16L', 'I;16B', 'I;16N']
