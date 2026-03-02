ProfileLineByLine("simple_tree.json");

d := function()
    Print("Hello World");
end;

b := function()
    d();
end;

c := function()
    d();
end;

# top level function
a := function()
    b();
    c();
end;

a();

UnprofileLineByLine();
QUIT;