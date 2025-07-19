cmake_minimum_required(VERSION 3.28)
project(minimal_kokkos CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

find_package(Kokkos REQUIRED)
find_package(Boost REQUIRED COMPONENTS serialization)

add_executable(main src/main.cpp)

target_link_libraries(main PRIVATE Kokkos::kokkos Boost::serialization)
