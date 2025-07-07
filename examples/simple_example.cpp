#include <Kokkos_Core.hpp>
#include <iostream>

int
main(int argc, char* argv[])
{
  Kokkos::initialize(argc, argv);
  {
    const int N = 10;
    Kokkos::parallel_for(
        "HelloLoop", N,
        KOKKOS_LAMBDA(int i) { printf("Hello from iteration %d\n", i); });
    Kokkos::fence();
  }
  Kokkos::finalize();
  return 0;
}