// Construct various pathnames using patterns and (Python) parameters.

#include <Python.h>

#include <stdio.h>
#include <string.h>
#include <strings.h>
#include <unistd.h>
#include "samlib.h"
#include "samutil.h"
#include "sam_param.h"

// Copy pattern, with replacements, into path.

// For example, a pattern of "%M/%P/%s" is the default for files
// in the MRI directory.

// ~ is the value of $HOME
// %M is MRIDirectory
// %P is setname[:Prefix]
// %s is the passed name
// %d is the dataset name
// %H is the hash code (first _ delimited field of setname)
// %S is the study (second _ field)
// %D is the date (third)
// %R is the run (fourth)

// path is output, using the given pattern. name may override the pattern.
// len is the size of the path buffer, and must be large enough.

int GetMRIPath(char *path, int len, PyObject *p, char *name)
{
    int i, ret = TRUE;
    char *s;

    i = 1;
    if (!param_getstr(p, "MRIPattern", &s)) {
        PyErr_Clear();
        s = "%M/%P/%s";
        i = 0;
    }
    if (!GetFilePath(s, path, len, p, name)) {
        ret = FALSE;
    }
    if (i) {
        free(s);
    }
    return ret;
}

int GetFilePath(char *pattern, char *path, int len, PyObject *p, char *name)
{
    int i, ret;
    char *r, *s, *t, *dsname, *setname, *home;
    char *f[4];     // H, S, D, and R pointers

    // If name is absolute or contains metacharacters, it overrides the pattern.

    i = FALSE;
    for (s = name; *s; s++) {
        if (*s == '%') {
            i = TRUE;
        }
    }
    if (i || name[0] == '/' || name[0] == '~') {
        pattern = name;
        name = "";          // so %s does nothing
    }

    // Parse the setname, for %H, etc. Up to 4 underscore delimited fields.

    if (!param_getstr(p, "DataSet", &dsname)) {
        return FALSE;
    }
    if (!param_getstr(p, "SetName", &setname)) {
        free(dsname);
        return FALSE;
    }

    s = setname;
    i = strlen(s) + 1;
    t = new_string(i);
    f[0] = t;
    i = 1;
    while (*s) {
        if (*s == '_' && i < 4) {
            *t++ = '\0';
            f[i] = t;
            i++;
        } else {
            *t++ = *s;
        }
        s++;
    }
    *t = '\0';

    // Make sure all 4 fields are filled in.

    while (i < 4) {     // set the rest to empty strings
        f[i++] = t;
    }

    // Parse the pattern, output what it says.

    s = pattern;
    t = path;

    if (*s == '~') {
        home = getenv("HOME");
        if (home) {
            // @@@ should check the length
            t = strecpy(t, home);
        }
        s++;
    }

    while (*s) {
        if (*s != '%') {
            *t++ = *s++;
        } else {
            s++;
            if (*s == 'M') {
                if (!param_getstr(p, "MRIDirectory", &r)) {
                    ret = FALSE;
                    goto fail;
                }
                t = strecpy(t, r);
                free(r);
            } else if (*s == 'P') {
                if (!param_getint(p, "Prefix", &i)) {
                    ret = FALSE;
                    goto fail;
                }
                strncpy(t, setname, i);
                t += i;
                *t = '\0';
            } else if (*s == 's') {
                t = strecpy(t, name);
            } else if (*s == 'd') {
                t = strecpy(t, dsname);
            } else if (*s == 'H') {
                t = strecpy(t, f[0]);
            } else if (*s == 'S') {
                t = strecpy(t, f[1]);
            } else if (*s == 'D') {
                t = strecpy(t, f[2]);
            } else if (*s == 'R') {
                t = strecpy(t, f[3]);
            }
            s++;
        }
    }
    *t = '\0';
    if (t >= path + len) {  // we already borked it @@@ should fix this
        fatalerr("filename too long: %s", path);
    }
    ret = TRUE;
fail:
    free(f[0]);
    free(dsname);
    free(setname);
    return ret;
}
