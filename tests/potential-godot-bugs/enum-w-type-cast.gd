enum Named { Foo, Bar = 1 if true else 0 }  # ok
enum Named2 { Foo, Bar = 1 << 3 }  # ok
enum Named3 { Foo, Bar = 1.5 as int }  # nok, why?
