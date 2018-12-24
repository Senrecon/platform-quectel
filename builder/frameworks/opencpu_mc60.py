# WizIO 2018 Georgi Angelov
# http://www.wizio.eu/
# https://github.com/Wiz-IO

from os.path import join
from SCons.Script import ARGUMENTS, DefaultEnvironment, Builder
from bin_mc60 import makeHDR, makeCFG

def mc60_header(target, source, env):
    makeHDR( source[0].path )
    makeCFG( source[0].path )

def mc60_init(env):
    TOOL_DIR = env.PioPlatform().get_package_dir("tool-opencpu")
    CORE = env.BoardConfig().get("build.core") # "mc60"
    CORE_DIR = join(env.PioPlatform().get_package_dir("framework-quectel"), "opencpu", CORE)    

    env.Append(
        CPPDEFINES=[ "CORE_"+CORE.upper() ], # -D
        CPPPATH=[ # -I
            CORE_DIR,
            join(CORE_DIR, "include"),
            join(CORE_DIR, "ril", "inc"),
            join(CORE_DIR, "fota", "inc"),        
        ],
        CFLAGS=[
            "-march=armv5te",
            "-mfloat-abi=soft",
            "-mfpu=vfp",
            "-fsingle-precision-constant",        
            "-mthumb",
            "-mthumb-interwork",        
            "-std=c99",
            "-Os",  
            "-Wall",
            "-fno-builtin",
            "-Wstrict-prototypes",
            "-Wp,-w",           
        ],

        LINKFLAGS=[        
            "-march=armv5te",
            "-mfloat-abi=soft",
            "-mfpu=vfp",
            "-mthumb",
            "-mthumb-interwork",   
            "-nostartfiles",     
            "-Rbuild",        
            "-Wl,--gc-sections,--relax", 
        ],
        LIBPATH=[CORE_DIR],
        LDSCRIPT_PATH=join(CORE_DIR, "linkscript.ld"),    
        LIBS=[ "gcc", "m", "app_start" ],

        BUILDERS=dict(
            ElfToBin=Builder(
                action=env.VerboseAction(" ".join([
                    "$OBJCOPY",
                    "-O", 
                    "binary",
                    "$SOURCES",
                    "$TARGET"
                ]), "Building $TARGET"),
                suffix=".dat"
            ),     
            MakeHeader=Builder( # Add Mediatek Header
                action = mc60_header, 
                suffix = ".bin"
            )        
        ), #dict

        UPLOADER=join(".", TOOL_DIR, "QFlash_V4.0", "QFlash_V4.0"), # We are waithing Quectel for console uploader
        UPLOADERFLAGS=[], # https://ss64.com/nt/start.html
        UPLOADCMD='START /D ' + TOOL_DIR + '\\QFlash_V4.0 /W QFlash_V4.0.exe', 
    ) # env.Append 

    libs = []
    libs.append(
        env.BuildLibrary(
            join("$BUILD_DIR", "framework"),
            join( CORE_DIR )
    ))
    libs.append(
        env.BuildLibrary(
            join("$BUILD_DIR", "framework", "ril"),
            join(CORE_DIR, "ril", "src")
    ))
    libs.append(
        env.BuildLibrary(
            join("$BUILD_DIR", "framework", "fota"),
            join(CORE_DIR, "fota", "src")
    ))
    env.Append( LIBS=libs )    