cmake_minimum_required(VERSION 3.28)
project(minimal_kokkos C CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

find_package(Kokkos REQUIRED)
find_package(Boost REQUIRED COMPONENTS serialization)
find_package(LLVM REQUIRED CONFIG)
find_package(Clang REQUIRED CONFIG)

include_directories(SYSTEM ${LLVM_INCLUDE_DIRS} ${CLANG_INCLUDE_DIRS})
add_definitions(${LLVM_DEFINITIONS})
add_executable(main src/main.cpp)
target_link_libraries(main PRIVATE Kokkos::kokkos Boost::serialization)
target_link_libraries(main PRIVATE clangTooling clangFrontend clangASTMatchers
                                   clangAST clangBasic clangLex)
add_subdirectory(examples)
