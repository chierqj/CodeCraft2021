# CMake 最低版本号要求
cmake_minimum_required(VERSION 2.8)

# 项目信息
project("CodeCraft-2021")

# include路径
include_directories(
    ${PROJECT_SOURCE_DIR}/
    ${PROJECT_SOURCE_DIR}/scenario
    ${PROJECT_SOURCE_DIR}/strategy
)

# 设置可执行文件生成路径
set(EXECUTABLE_OUTPUT_PATH ${PROJECT_BINARY_DIR}/../bin)
set(CMAKE_EXE_LINKER_FLAGS -static)
# 生成debug版本
# SET(CMAKE_BUILD_TYPE "debug")
# 生成release版本
SET(CMAKE_BUILD_TYPE "release")
if (CMAKE_BUILD_TYPE STREQUAL debug)
    add_definitions(-D_DEBUG)
endif ()

SET(CMAKE_CXX_FLAGS_DEBUG "$ENV{CXXFLAGS} -O0 -Wall -g -ggdb -std=c++11")
SET(CMAKE_CXX_FLAGS_RELEASE "$ENV{CXXFLAGS} -O3 -Wall -std=c++11")

option(LOCAL_DEBUG "option for debug" OFF)
if (LOCAL_DEBUG) 
	add_definitions(-DLOCAL_DEBUG)
endif(LOCAL_DEBUG)

# 查找当前目录下的所有源文件
# 并将名称保存到 DIR_LIB_SRCS 变量
aux_source_directory(. DIR_SRCS)
aux_source_directory(scenario DIR_SRCS)
aux_source_directory(strategy DIR_SRCS)

# 指定生成目标
add_executable(CodeCraft-2021 ${DIR_SRCS})