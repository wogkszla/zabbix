# Test Runner

The automated tests under `tests/` are executed by the Perl script `tests_run.pl`.

## Perl dependencies

The script requires several CPAN modules:

- `YAML::XS`
- `IPC::Run3`
- `Path::Tiny`
- `Term::ANSIColor` (for colored output)
- `Time::HiRes`
- `File::Basename`
- `Getopt::Long`
- `Cwd`
- `Pod::Usage`

`Time::HiRes`, `File::Basename`, `Getopt::Long`, `Cwd` and `Pod::Usage` are shipped with the default Perl distribution, while `YAML::XS`, `IPC::Run3`, `Path::Tiny` and `Term::ANSIColor` may need to be installed from your package manager or CPAN.

## Installing on Ubuntu 22.04

On Ubuntu 22.04 the required modules can be installed via `apt`:

```bash
sudo apt update
sudo apt install libyaml-libyaml-perl libipc-run3-perl libpath-tiny-perl libterm-ansicolor-perl
```

After installing the dependencies run the tests using:

```bash
./tests/tests_run.pl
```
