ProfileLineByLine("error_multi_level.json");

a := function()
    Error();
end;

b := function()
end;

c := function()
    BreakOnError := false;
    CALL_WITH_CATCH(a, []);
    b();
end;

c();

UnprofileLineByLine();
QUIT;