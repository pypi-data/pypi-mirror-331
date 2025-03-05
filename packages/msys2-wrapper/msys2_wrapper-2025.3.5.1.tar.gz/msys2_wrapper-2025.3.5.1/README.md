# msys2_wrapper

A Python wrapper for starting msys2 without bat

## Prereq

Has installed MSYS2 at disk root (e.g. `C:/msys64`), or `msys2.cmd` or `msys2_shell.cmd` can be found in PATH.

also supports scoop-installed msys2.

In case of multiple MSYS2 detected, it will launch the first found in `PATH`, and if not found, `C:/msys64` was checked, until `Z:/msys64`.

You can also create a file `C:/Users/[your user name]/.config/msys2_wrapper.ini` to override the default, with the following contents:
```ini
[default]
base = "D:/msys64"
```

## Usage

A console launcher:

```
msys2c /?
Usage:
    msys2c [options] [login shell parameters]

Options:
    -mingw32 | -mingw64 | -ucrt64 | -clang64 |
    -msys[2] | -clangarm64           Set shell type
    -defterm | -mintty | -conemu     Set terminal type
    -here                            Use current directory as working
                                     directory
    -where DIRECTORY                 Use specified DIRECTORY as working
                                     directory
    -[use-]full-path                 Use full current PATH variable
                                     instead of trimming to minimal
    -no-start                        Do not use "start" command and
                                     return login shell resulting
                                     errorcode as this batch file
                                     resulting errorcode
    -shell SHELL                     Set login shell
    -search PACKAGE                  search pacakge using web browser
    -help | --help | -? | /?         Display this help and exit

Any parameter that cannot be treated as valid option and all
following parameters are passed as login shell command parameters.
```

A GUI launcher `msys2w` was provided for launch with default `mintty` .

## Source code

<https://github.com/soda92/msys2_wrapper>

## License

APACHE