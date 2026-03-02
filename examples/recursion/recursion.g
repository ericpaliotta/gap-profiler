ProfileLineByLine("recursion.json");

levels := 1000;

a := function()
    if levels = 0 then
        return;
    else
        levels := levels - 1;
        a();
    fi;
end;

a();

UnprofileLineByLine();
QUIT;