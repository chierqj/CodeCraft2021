# CMAKE generated file: DO NOT EDIT!
# Generated by "Unix Makefiles" Generator, CMake Version 3.19

# Delete rule output on recipe failure.
.DELETE_ON_ERROR:


#=============================================================================
# Special targets provided by cmake.

# Disable implicit rules so canonical targets will work.
.SUFFIXES:


# Disable VCS-based implicit rules.
% : %,v


# Disable VCS-based implicit rules.
% : RCS/%


# Disable VCS-based implicit rules.
% : RCS/%,v


# Disable VCS-based implicit rules.
% : SCCS/s.%


# Disable VCS-based implicit rules.
% : s.%


.SUFFIXES: .hpux_make_needs_suffix_list


# Command-line flag to silence nested $(MAKE).
$(VERBOSE)MAKESILENT = -s

#Suppress display of executed commands.
$(VERBOSE).SILENT:

# A target that is always out of date.
cmake_force:

.PHONY : cmake_force

#=============================================================================
# Set environment variables for the build.

# The shell in which to execute make rules.
SHELL = /bin/sh

# The CMake executable.
CMAKE_COMMAND = D:/cmake/bin/cmake.exe

# The command to remove a file.
RM = D:/cmake/bin/cmake.exe -E rm -f

# Escaping for special characters.
EQUALS = =

# The top-level source directory on which CMake was run.
CMAKE_SOURCE_DIR = E:/CodeCraft2021/src/CodeCraft-2021

# The top-level build directory on which CMake was run.
CMAKE_BINARY_DIR = E:/CodeCraft2021/src/build

# Include any dependencies generated for this target.
include CMakeFiles/CodeCraft-2021.dir/depend.make

# Include the progress variables for this target.
include CMakeFiles/CodeCraft-2021.dir/progress.make

# Include the compile flags for this target's objects.
include CMakeFiles/CodeCraft-2021.dir/flags.make

CMakeFiles/CodeCraft-2021.dir/CodeCraft-2021.cpp.obj: CMakeFiles/CodeCraft-2021.dir/flags.make
CMakeFiles/CodeCraft-2021.dir/CodeCraft-2021.cpp.obj: CMakeFiles/CodeCraft-2021.dir/includes_CXX.rsp
CMakeFiles/CodeCraft-2021.dir/CodeCraft-2021.cpp.obj: E:/CodeCraft2021/src/CodeCraft-2021/CodeCraft-2021.cpp
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --progress-dir=E:/CodeCraft2021/src/build/CMakeFiles --progress-num=$(CMAKE_PROGRESS_1) "Building CXX object CMakeFiles/CodeCraft-2021.dir/CodeCraft-2021.cpp.obj"
	D:/mingw64/bin/c++.exe $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -o CMakeFiles/CodeCraft-2021.dir/CodeCraft-2021.cpp.obj -c E:/CodeCraft2021/src/CodeCraft-2021/CodeCraft-2021.cpp

CMakeFiles/CodeCraft-2021.dir/CodeCraft-2021.cpp.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Preprocessing CXX source to CMakeFiles/CodeCraft-2021.dir/CodeCraft-2021.cpp.i"
	D:/mingw64/bin/c++.exe $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -E E:/CodeCraft2021/src/CodeCraft-2021/CodeCraft-2021.cpp > CMakeFiles/CodeCraft-2021.dir/CodeCraft-2021.cpp.i

CMakeFiles/CodeCraft-2021.dir/CodeCraft-2021.cpp.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Compiling CXX source to assembly CMakeFiles/CodeCraft-2021.dir/CodeCraft-2021.cpp.s"
	D:/mingw64/bin/c++.exe $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -S E:/CodeCraft2021/src/CodeCraft-2021/CodeCraft-2021.cpp -o CMakeFiles/CodeCraft-2021.dir/CodeCraft-2021.cpp.s

CMakeFiles/CodeCraft-2021.dir/scenario/log.cpp.obj: CMakeFiles/CodeCraft-2021.dir/flags.make
CMakeFiles/CodeCraft-2021.dir/scenario/log.cpp.obj: CMakeFiles/CodeCraft-2021.dir/includes_CXX.rsp
CMakeFiles/CodeCraft-2021.dir/scenario/log.cpp.obj: E:/CodeCraft2021/src/CodeCraft-2021/scenario/log.cpp
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --progress-dir=E:/CodeCraft2021/src/build/CMakeFiles --progress-num=$(CMAKE_PROGRESS_2) "Building CXX object CMakeFiles/CodeCraft-2021.dir/scenario/log.cpp.obj"
	D:/mingw64/bin/c++.exe $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -o CMakeFiles/CodeCraft-2021.dir/scenario/log.cpp.obj -c E:/CodeCraft2021/src/CodeCraft-2021/scenario/log.cpp

CMakeFiles/CodeCraft-2021.dir/scenario/log.cpp.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Preprocessing CXX source to CMakeFiles/CodeCraft-2021.dir/scenario/log.cpp.i"
	D:/mingw64/bin/c++.exe $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -E E:/CodeCraft2021/src/CodeCraft-2021/scenario/log.cpp > CMakeFiles/CodeCraft-2021.dir/scenario/log.cpp.i

CMakeFiles/CodeCraft-2021.dir/scenario/log.cpp.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Compiling CXX source to assembly CMakeFiles/CodeCraft-2021.dir/scenario/log.cpp.s"
	D:/mingw64/bin/c++.exe $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -S E:/CodeCraft2021/src/CodeCraft-2021/scenario/log.cpp -o CMakeFiles/CodeCraft-2021.dir/scenario/log.cpp.s

CMakeFiles/CodeCraft-2021.dir/scenario/server.cpp.obj: CMakeFiles/CodeCraft-2021.dir/flags.make
CMakeFiles/CodeCraft-2021.dir/scenario/server.cpp.obj: CMakeFiles/CodeCraft-2021.dir/includes_CXX.rsp
CMakeFiles/CodeCraft-2021.dir/scenario/server.cpp.obj: E:/CodeCraft2021/src/CodeCraft-2021/scenario/server.cpp
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --progress-dir=E:/CodeCraft2021/src/build/CMakeFiles --progress-num=$(CMAKE_PROGRESS_3) "Building CXX object CMakeFiles/CodeCraft-2021.dir/scenario/server.cpp.obj"
	D:/mingw64/bin/c++.exe $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -o CMakeFiles/CodeCraft-2021.dir/scenario/server.cpp.obj -c E:/CodeCraft2021/src/CodeCraft-2021/scenario/server.cpp

CMakeFiles/CodeCraft-2021.dir/scenario/server.cpp.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Preprocessing CXX source to CMakeFiles/CodeCraft-2021.dir/scenario/server.cpp.i"
	D:/mingw64/bin/c++.exe $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -E E:/CodeCraft2021/src/CodeCraft-2021/scenario/server.cpp > CMakeFiles/CodeCraft-2021.dir/scenario/server.cpp.i

CMakeFiles/CodeCraft-2021.dir/scenario/server.cpp.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Compiling CXX source to assembly CMakeFiles/CodeCraft-2021.dir/scenario/server.cpp.s"
	D:/mingw64/bin/c++.exe $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -S E:/CodeCraft2021/src/CodeCraft-2021/scenario/server.cpp -o CMakeFiles/CodeCraft-2021.dir/scenario/server.cpp.s

CMakeFiles/CodeCraft-2021.dir/strategy/greedy.cpp.obj: CMakeFiles/CodeCraft-2021.dir/flags.make
CMakeFiles/CodeCraft-2021.dir/strategy/greedy.cpp.obj: CMakeFiles/CodeCraft-2021.dir/includes_CXX.rsp
CMakeFiles/CodeCraft-2021.dir/strategy/greedy.cpp.obj: E:/CodeCraft2021/src/CodeCraft-2021/strategy/greedy.cpp
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --progress-dir=E:/CodeCraft2021/src/build/CMakeFiles --progress-num=$(CMAKE_PROGRESS_4) "Building CXX object CMakeFiles/CodeCraft-2021.dir/strategy/greedy.cpp.obj"
	D:/mingw64/bin/c++.exe $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -o CMakeFiles/CodeCraft-2021.dir/strategy/greedy.cpp.obj -c E:/CodeCraft2021/src/CodeCraft-2021/strategy/greedy.cpp

CMakeFiles/CodeCraft-2021.dir/strategy/greedy.cpp.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Preprocessing CXX source to CMakeFiles/CodeCraft-2021.dir/strategy/greedy.cpp.i"
	D:/mingw64/bin/c++.exe $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -E E:/CodeCraft2021/src/CodeCraft-2021/strategy/greedy.cpp > CMakeFiles/CodeCraft-2021.dir/strategy/greedy.cpp.i

CMakeFiles/CodeCraft-2021.dir/strategy/greedy.cpp.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Compiling CXX source to assembly CMakeFiles/CodeCraft-2021.dir/strategy/greedy.cpp.s"
	D:/mingw64/bin/c++.exe $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -S E:/CodeCraft2021/src/CodeCraft-2021/strategy/greedy.cpp -o CMakeFiles/CodeCraft-2021.dir/strategy/greedy.cpp.s

CMakeFiles/CodeCraft-2021.dir/strategy/purchase.cpp.obj: CMakeFiles/CodeCraft-2021.dir/flags.make
CMakeFiles/CodeCraft-2021.dir/strategy/purchase.cpp.obj: CMakeFiles/CodeCraft-2021.dir/includes_CXX.rsp
CMakeFiles/CodeCraft-2021.dir/strategy/purchase.cpp.obj: E:/CodeCraft2021/src/CodeCraft-2021/strategy/purchase.cpp
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --progress-dir=E:/CodeCraft2021/src/build/CMakeFiles --progress-num=$(CMAKE_PROGRESS_5) "Building CXX object CMakeFiles/CodeCraft-2021.dir/strategy/purchase.cpp.obj"
	D:/mingw64/bin/c++.exe $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -o CMakeFiles/CodeCraft-2021.dir/strategy/purchase.cpp.obj -c E:/CodeCraft2021/src/CodeCraft-2021/strategy/purchase.cpp

CMakeFiles/CodeCraft-2021.dir/strategy/purchase.cpp.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Preprocessing CXX source to CMakeFiles/CodeCraft-2021.dir/strategy/purchase.cpp.i"
	D:/mingw64/bin/c++.exe $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -E E:/CodeCraft2021/src/CodeCraft-2021/strategy/purchase.cpp > CMakeFiles/CodeCraft-2021.dir/strategy/purchase.cpp.i

CMakeFiles/CodeCraft-2021.dir/strategy/purchase.cpp.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Compiling CXX source to assembly CMakeFiles/CodeCraft-2021.dir/strategy/purchase.cpp.s"
	D:/mingw64/bin/c++.exe $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -S E:/CodeCraft2021/src/CodeCraft-2021/strategy/purchase.cpp -o CMakeFiles/CodeCraft-2021.dir/strategy/purchase.cpp.s

# Object files for target CodeCraft-2021
CodeCraft__2021_OBJECTS = \
"CMakeFiles/CodeCraft-2021.dir/CodeCraft-2021.cpp.obj" \
"CMakeFiles/CodeCraft-2021.dir/scenario/log.cpp.obj" \
"CMakeFiles/CodeCraft-2021.dir/scenario/server.cpp.obj" \
"CMakeFiles/CodeCraft-2021.dir/strategy/greedy.cpp.obj" \
"CMakeFiles/CodeCraft-2021.dir/strategy/purchase.cpp.obj"

# External object files for target CodeCraft-2021
CodeCraft__2021_EXTERNAL_OBJECTS =

E:/CodeCraft2021/src/bin/CodeCraft-2021.exe: CMakeFiles/CodeCraft-2021.dir/CodeCraft-2021.cpp.obj
E:/CodeCraft2021/src/bin/CodeCraft-2021.exe: CMakeFiles/CodeCraft-2021.dir/scenario/log.cpp.obj
E:/CodeCraft2021/src/bin/CodeCraft-2021.exe: CMakeFiles/CodeCraft-2021.dir/scenario/server.cpp.obj
E:/CodeCraft2021/src/bin/CodeCraft-2021.exe: CMakeFiles/CodeCraft-2021.dir/strategy/greedy.cpp.obj
E:/CodeCraft2021/src/bin/CodeCraft-2021.exe: CMakeFiles/CodeCraft-2021.dir/strategy/purchase.cpp.obj
E:/CodeCraft2021/src/bin/CodeCraft-2021.exe: CMakeFiles/CodeCraft-2021.dir/build.make
E:/CodeCraft2021/src/bin/CodeCraft-2021.exe: CMakeFiles/CodeCraft-2021.dir/linklibs.rsp
E:/CodeCraft2021/src/bin/CodeCraft-2021.exe: CMakeFiles/CodeCraft-2021.dir/objects1.rsp
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --bold --progress-dir=E:/CodeCraft2021/src/build/CMakeFiles --progress-num=$(CMAKE_PROGRESS_6) "Linking CXX executable E:/CodeCraft2021/src/bin/CodeCraft-2021.exe"
	D:/cmake/bin/cmake.exe -E rm -f CMakeFiles/CodeCraft-2021.dir/objects.a
	D:/mingw64/bin/ar.exe cr CMakeFiles/CodeCraft-2021.dir/objects.a @CMakeFiles/CodeCraft-2021.dir/objects1.rsp
	D:/mingw64/bin/c++.exe  -O3 -Wall -std=c++11 -static -Wl,--whole-archive CMakeFiles/CodeCraft-2021.dir/objects.a -Wl,--no-whole-archive -o E:/CodeCraft2021/src/bin/CodeCraft-2021.exe -Wl,--out-implib,E:/CodeCraft2021/src/bin/libCodeCraft-2021.dll.a -Wl,--major-image-version,0,--minor-image-version,0 @CMakeFiles/CodeCraft-2021.dir/linklibs.rsp

# Rule to build all files generated by this target.
CMakeFiles/CodeCraft-2021.dir/build: E:/CodeCraft2021/src/bin/CodeCraft-2021.exe

.PHONY : CMakeFiles/CodeCraft-2021.dir/build

CMakeFiles/CodeCraft-2021.dir/clean:
	$(CMAKE_COMMAND) -P CMakeFiles/CodeCraft-2021.dir/cmake_clean.cmake
.PHONY : CMakeFiles/CodeCraft-2021.dir/clean

CMakeFiles/CodeCraft-2021.dir/depend:
	$(CMAKE_COMMAND) -E cmake_depends "Unix Makefiles" E:/CodeCraft2021/src/CodeCraft-2021 E:/CodeCraft2021/src/CodeCraft-2021 E:/CodeCraft2021/src/build E:/CodeCraft2021/src/build E:/CodeCraft2021/src/build/CMakeFiles/CodeCraft-2021.dir/DependInfo.cmake --color=$(COLOR)
.PHONY : CMakeFiles/CodeCraft-2021.dir/depend
