#include <nanobind/nanobind.h>

NB_MODULE(_smoke, m)
{
    m.def("answer", [] { return 42; });
}
