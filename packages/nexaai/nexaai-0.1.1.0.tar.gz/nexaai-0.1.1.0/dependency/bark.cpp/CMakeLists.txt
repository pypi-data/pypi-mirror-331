cmake_minimum_required(VERSION 3.12)
project("bark" C CXX)

option(BARK_BUILD_EXAMPLES "Build examples" ON)
option(BUILD_SHARED_LIBS "Build shared libraries" ON)

if (NOT XCODE AND NOT MSVC AND NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release CACHE STRING "Build type" FORCE)
    set_property(CACHE CMAKE_BUILD_TYPE PROPERTY STRINGS "Debug" "Release" "MinSizeRel" "RelWithDebInfo")
endif()

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
set(CMAKE_CXX_FLAGS_RELEASE "-O3")

if (EMSCRIPTEN)
    set(CMAKE_C_FLAGS   "${CMAKE_C_FLAGS}   -pthread -O3")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -pthread -O3")
endif()

set(BARK_LIB bark)

add_subdirectory(encodec.cpp)

# Override the output name of ggml
set_target_properties(ggml PROPERTIES OUTPUT_NAME "ggml-bark") # Rename ggml to ggml-bark

# Build either shared or static library based on BUILD_SHARED_LIBS
if(BUILD_SHARED_LIBS)
    add_library(${BARK_LIB} SHARED bark.cpp bark.h)
    set_target_properties(${BARK_LIB} PROPERTIES 
                            PUBLIC_HEADER bark.h
                            POSITION_INDEPENDENT_CODE ON
    )
    
    # Add EXPORTING_BARK definition when building the shared library
    target_compile_definitions(${BARK_LIB} PRIVATE EXPORTING_BARK)
    
    # Ensure all symbols are exported on Windows
    if(MSVC)
        set_target_properties(${BARK_LIB} PROPERTIES WINDOWS_EXPORT_ALL_SYMBOLS ON)
    endif()
else()
    add_library(${BARK_LIB} STATIC bark.cpp bark.h)
endif()

if (BARK_BUILD_EXAMPLES)
    add_subdirectory(examples)
endif()

# Note: "ggml" is the internal target name in CMake, its output file name has been changed to "ggml-bark".
target_link_libraries(${BARK_LIB} PUBLIC ggml encodec)
target_include_directories(${BARK_LIB} PUBLIC .)
target_compile_features(${BARK_LIB} PUBLIC cxx_std_11)

if (EMSCRIPTEN)
    set_target_properties(${BARK_LIB} PROPERTIES COMPILE_FLAGS "-msimd128")
endif()

if (GGML_CUBLAS)
    add_compile_definitions(GGML_USE_CUBLAS)
endif()

if (GGML_METAL)
    add_compile_definitions(GGML_USE_METAL)
endif()

# Ensure ggml and encodec are built with position-independent code
set_target_properties(ggml PROPERTIES POSITION_INDEPENDENT_CODE ON)
set_target_properties(encodec PROPERTIES POSITION_INDEPENDENT_CODE ON)

# Install the libraries
install(TARGETS ${BARK_LIB}
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib
    RUNTIME DESTINATION bin
)

# Install header files
install(FILES bark.h DESTINATION include)