
import errno
import glob
import multiprocessing
import os
import subprocess
import sys

CONFIGS = {}
script_dir = os.path.dirname(__file__)

# Cargar configuraciones
for config_file in sorted(glob.glob(os.path.join(script_dir, "*build_configs.py"))):
    try:
        with open(config_file) as f:
            config_file_content = f.read()
        # Ejecutar el contenido del archivo de configuración
        exec(config_file_content, globals(), CONFIGS)
    except Exception as e:
        print(f"Error loading config file {config_file}: {e}")
        sys.exit(1)

DEFAULT_CONFIG_NAME = CONFIGS.pop("DEFAULT", "release")
DEBUG_CONFIG_NAME = CONFIGS.pop("DEBUG", "debug")

# Configuración de herramientas de build
CMAKE = "cmake"
DEFAULT_MAKE_PARAMETERS = []

if os.name == "posix":
    MAKE = "make"
    try:
        num_cpus = multiprocessing.cpu_count()
        DEFAULT_MAKE_PARAMETERS.append(f'-j{num_cpus}')
    except NotImplementedError:
        pass
    CMAKE_GENERATOR = "Unix Makefiles"
elif os.name == "nt":
    MAKE = "nmake"
    CMAKE_GENERATOR = "NMake Makefiles"
else:
    print(f"Unsupported OS: {os.name}")
    sys.exit(1)


def print_usage():
    script_name = os.path.basename(__file__)
    configs = []
    
    for name, args in sorted(CONFIGS.items()):
        display_name = name
        if name == DEFAULT_CONFIG_NAME:
            display_name += " (default)"
        if name == DEBUG_CONFIG_NAME:
            display_name += " (default with --debug)"
        configs.append(f"{display_name}\n    {' '.join(args)}")
    
    configs_string = "\n  ".join(configs)
    
    print(f"""Usage: {script_name} [BUILD [BUILD ...]] [--all] [--debug] [MAKE_OPTIONS]

Build one or more predefined build configurations of Fast Downward. Each build
uses {os.path.basename(CMAKE)} to generate {CMAKE_GENERATOR.lower()} and then uses {os.path.basename(MAKE)} to compile the
code. Build configurations differ in the parameters they pass to {os.path.basename(CMAKE)}.
By default, the build uses N threads on a machine with N cores if the number of
cores can be determined. Use the "-j" option for {os.path.basename(CMAKE)} to override this default
behaviour.

Build configurations
  {configs_string}

--all         Alias to build all build configurations.
--debug       Alias to build the default debug build configuration.
--help        Print this message and exit.

Make options
  All other parameters are forwarded to {os.path.basename(MAKE)}.

Example usage:
  ./{script_name}                     # build {DEFAULT_CONFIG_NAME} in #cores threads
  ./{script_name} -j4                 # build {DEFAULT_CONFIG_NAME} in 4 threads
  ./{script_name} {DEBUG_CONFIG_NAME}             # build {DEBUG_CONFIG_NAME}
  ./{script_name} --debug             # build {DEBUG_CONFIG_NAME}
  ./{script_name} release64 debug64   # build both 64-bit build configs
  ./{script_name} --all VERBOSE=true  # build all build configs with detailed logs
""")


def get_project_root_path():
    import __main__
    return os.path.dirname(__main__.__file__)


def get_builds_path():
    return os.path.join(get_project_root_path(), "builds")


def get_src_path():
    return os.path.join(get_project_root_path(), "src")


def get_build_path(config_name):
    return os.path.join(get_builds_path(), config_name)


def try_run(cmd, cwd):
    print(f'Executing command "{" ".join(cmd)}" in directory "{cwd}".')
    try:
        subprocess.check_call(cmd, cwd=cwd)
    except OSError as exc:
        if exc.errno == errno.ENOENT:
            print(f"Could not find '{cmd[0]}' on your PATH. For installation instructions, "
                  "see http://www.fast-downward.org/ObtainingAndRunningFastDownward.")
            sys.exit(1)
        else:
            raise
    except subprocess.CalledProcessError as e:
        print(f"Command failed with exit code {e.returncode}")
        sys.exit(e.returncode)


def build(config_name, cmake_parameters, make_parameters):
    print(f"Building configuration {config_name}.")
    build_path = get_build_path(config_name)
    rel_src_path = os.path.relpath(get_src_path(), build_path)
    
    try:
        os.makedirs(build_path, exist_ok=True)
    except OSError as e:
        print(f"Error creating directory {build_path}: {e}")
        sys.exit(1)

    try_run([CMAKE, "-G", CMAKE_GENERATOR] + cmake_parameters + [rel_src_path],
            cwd=build_path)
    try_run([MAKE] + make_parameters, cwd=build_path)

    print(f"Built configuration {config_name} successfully.")


def main():
    config_names = set()
    make_parameters = DEFAULT_MAKE_PARAMETERS.copy()  # Usar copia para no modificar la original
    
    for arg in sys.argv[1:]:
        if arg in ["--help", "-h"]:
            print_usage()
            sys.exit(0)
        elif arg == "--debug":
            config_names.add(DEBUG_CONFIG_NAME)
        elif arg == "--all":
            config_names.update(CONFIGS.keys())
        elif arg in CONFIGS:
            config_names.add(arg)
        else:
            make_parameters.append(arg)
    
    if not config_names:
        config_names.add(DEFAULT_CONFIG_NAME)
    
    for config_name in config_names:
        build(config_name, CONFIGS[config_name], make_parameters)


    if __name__ == "__main__":
       main()