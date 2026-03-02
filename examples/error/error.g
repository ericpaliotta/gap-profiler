ProfileLineByLine("error.json");

a := function()
    Error();
end;
BreakOnError := false;
CALL_WITH_CATCH(a, []);

UnprofileLineByLine();
QUIT;