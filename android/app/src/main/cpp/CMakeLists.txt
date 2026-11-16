cmake_minimum_required(VERSION 3.22.1)
project(saturn_android C CXX)

set(CMAKE_C_STANDARD 99)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

set(SATURN_ROOT "${CMAKE_CURRENT_LIST_DIR}/../../../../..")
get_filename_component(SATURN_ROOT "${SATURN_ROOT}" ABSOLUTE)
set(SDL2_ROOT "${SATURN_ROOT}/android/SDL")

if(NOT EXISTS "${SDL2_ROOT}/CMakeLists.txt")
    message(FATAL_ERROR "SDL2 source missing. Run scripts/port_to_android.py first.")
endif()

set(SDL_SHARED ON CACHE BOOL "" FORCE)
set(SDL_STATIC OFF CACHE BOOL "" FORCE)
set(SDL_TEST OFF CACHE BOOL "" FORCE)
set(SDL_TESTS OFF CACHE BOOL "" FORCE)
set(SDL_INSTALL OFF CACHE BOOL "" FORCE)
add_subdirectory("${SDL2_ROOT}" "${CMAKE_CURRENT_BINARY_DIR}/SDL2")

file(GLOB_RECURSE SATURN_C CONFIGURE_DEPENDS
    "${SATURN_ROOT}/src/*.c"
    "${SATURN_ROOT}/actors/*.c"
    "${SATURN_ROOT}/levels/*.c")
file(GLOB_RECURSE SATURN_CXX CONFIGURE_DEPENDS
    "${SATURN_ROOT}/src/*.cpp"
    "${SATURN_ROOT}/actors/*.cpp"
    "${SATURN_ROOT}/levels/*.cpp")

set(SATURN_SOURCES ${SATURN_C} ${SATURN_CXX})
# .inc.c files are textually included by their owning actor/level source; they are not translation units.
list(FILTER SATURN_SOURCES EXCLUDE REGEX "\\.inc\\.c$")
list(FILTER SATURN_SOURCES EXCLUDE REGEX "/src/game/main\\.c$")
list(FILTER SATURN_SOURCES EXCLUDE REGEX "gfx_direct3d")
list(FILTER SATURN_SOURCES EXCLUDE REGEX "gfx_dxgi")
list(FILTER SATURN_SOURCES EXCLUDE REGEX "/discord/")
list(FILTER SATURN_SOURCES EXCLUDE REGEX "/src/pc/gfx/gfx_opengl_legacy\\.c$")

set(ULTRA_SOURCES
    "${SATURN_ROOT}/lib/src/alBnkfNew.c"
    "${SATURN_ROOT}/lib/src/guLookAtRef.c"
    "${SATURN_ROOT}/lib/src/guMtxF2L.c"
    "${SATURN_ROOT}/lib/src/guNormalize.c"
    "${SATURN_ROOT}/lib/src/guOrthoF.c"
    "${SATURN_ROOT}/lib/src/guPerspectiveF.c"
    "${SATURN_ROOT}/lib/src/guRotateF.c"
    "${SATURN_ROOT}/lib/src/guScaleF.c"
    "${SATURN_ROOT}/lib/src/guTranslateF.c"
    "${SATURN_ROOT}/lib/src/ldiv.c")

find_package(Python3 REQUIRED COMPONENTS Interpreter)

set(GENERATED_DIR "${CMAKE_CURRENT_BINARY_DIR}/generated")
file(MAKE_DIRECTORY "${GENERATED_DIR}/assets" "${GENERATED_DIR}/include")
add_custom_command(
    OUTPUT "${GENERATED_DIR}/assets/mario_anim_data.c"
    COMMAND /bin/sh -c
        "'${Python3_EXECUTABLE}' '${SATURN_ROOT}/tools/mario_anims_converter.py' > '${GENERATED_DIR}/assets/mario_anim_data.c'"
    WORKING_DIRECTORY "${SATURN_ROOT}"
    DEPENDS "${SATURN_ROOT}/tools/mario_anims_converter.py"
    VERBATIM)
add_custom_command(
    OUTPUT "${GENERATED_DIR}/include/level_headers.h"
    COMMAND /bin/sh -c
        "${CMAKE_C_COMPILER} -E -P -x c -DVERSION_US=1 -D_LANGUAGE_C -I '${SATURN_ROOT}/include' -I '${SATURN_ROOT}' '${SATURN_ROOT}/levels/level_headers.h.in' | python3 '${SATURN_ROOT}/tools/output_level_headers.py' > '${GENERATED_DIR}/include/level_headers.h'"
    WORKING_DIRECTORY "${SATURN_ROOT}"
    DEPENDS "${SATURN_ROOT}/levels/level_headers.h.in" "${SATURN_ROOT}/tools/output_level_headers.py"
    VERBATIM)

add_custom_command(
    OUTPUT "${GENERATED_DIR}/include/text_strings.h"
    COMMAND "${SATURN_ROOT}/tools/textconv" charmap.txt
            "${SATURN_ROOT}/include/text_strings.h.in"
            "${GENERATED_DIR}/include/text_strings.h"
    WORKING_DIRECTORY "${SATURN_ROOT}"
    DEPENDS "${SATURN_ROOT}/include/text_strings.h.in" "${SATURN_ROOT}/charmap.txt"
    VERBATIM)
add_custom_command(
    OUTPUT "${GENERATED_DIR}/include/text_menu_strings.h"
    COMMAND "${SATURN_ROOT}/tools/textconv" charmap_menu.txt
            "${SATURN_ROOT}/include/text_menu_strings.h.in"
            "${GENERATED_DIR}/include/text_menu_strings.h"
    WORKING_DIRECTORY "${SATURN_ROOT}"
    DEPENDS "${SATURN_ROOT}/include/text_menu_strings.h.in" "${SATURN_ROOT}/charmap_menu.txt"
    VERBATIM)
add_custom_command(
    OUTPUT "${GENERATED_DIR}/include/text_options_strings.h"
    COMMAND "${SATURN_ROOT}/tools/textconv" charmap.txt
            "${SATURN_ROOT}/include/text_options_strings.h.in"
            "${GENERATED_DIR}/include/text_options_strings.h"
    WORKING_DIRECTORY "${SATURN_ROOT}"
    DEPENDS "${SATURN_ROOT}/include/text_options_strings.h.in" "${SATURN_ROOT}/charmap.txt"
    VERBATIM)

add_custom_target(saturn_generated DEPENDS
    "${GENERATED_DIR}/assets/mario_anim_data.c"
    "${GENERATED_DIR}/include/level_headers.h"
    "${GENERATED_DIR}/include/text_strings.h"
    "${GENERATED_DIR}/include/text_menu_strings.h"
    "${GENERATED_DIR}/include/text_options_strings.h")

add_library(main SHARED
    ${SATURN_SOURCES}
    ${ULTRA_SOURCES}
    "${GENERATED_DIR}/assets/mario_anim_data.c")
add_dependencies(main saturn_generated)

target_include_directories(main PRIVATE
    "${SATURN_ROOT}"
    "${SATURN_ROOT}/include"
    "${CMAKE_CURRENT_LIST_DIR}/sdl2_include"
    "${SATURN_ROOT}/src"
    "${SATURN_ROOT}/lib/src"
    "${SATURN_ROOT}/build"
    "${GENERATED_DIR}"
    "${GENERATED_DIR}/include"
    "${SDL2_ROOT}/include")

target_compile_definitions(main PRIVATE
    VERSION_US=1
    _LANGUAGE_C=1
    NON_MATCHING=1
    AVOID_UB=1
    RAPI_GL=1
    WAPI_SDL2=1
    AAPI_SDL2=1
    CAPI_SDL2=1
    HAVE_SDL2=1
    USE_GLES=1
    EXTERNAL_DATA=1
    NODRAWINGDISTANCE=1
    TEXTURE_FIX=1
    EXT_OPTIONS_MENU=1
    NO_BZERO_BCOPY=1
    main=SDL_main)

target_compile_options(main PRIVATE
    -fno-strict-aliasing
    -fwrapv
    -Wno-unused-parameter
    -Wno-format-security
    -Wno-deprecated-declarations)

target_link_libraries(main PRIVATE
    SDL2
    GLESv2
    EGL
    android
    log
    z
    m
    dl)
