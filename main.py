import subprocess
from typing import List

def execute_adb_command(cmd: str) -> List[str]:
    process = subprocess.run(
        f"adb shell {cmd}",
        capture_output=True,
        shell=True
    )
    output = process.stdout.decode().split('\n')
    output.pop()
    return output

def list_files(folder: str) -> List[str]:
    files = execute_adb_command(f"ls {folder}")
    return list(map(lambda file : folder + "/" + file, files))

def list_dependencies(file: str, arch: str) -> List[str]:
    dependencies = execute_adb_command(f"linker{arch} --list {file}")
    return dependencies

partitions = [
    "/system",
    "/vendor",
    "/product",
    # "/system_ext",
    # "/apex/com.android.runtime"
]

archs = [
    # "",     #32 bits,
    "64"    #guess??
]

binaries_absolute_path = list()
binaries_index_to_dependencies_index = {}

for partition in partitions:
    for arch in archs:
        binaries = list_files(f"{partition}/lib{arch}")

        for binary in binaries:
            if binary not in binaries_absolute_path:
                binaries_absolute_path.append(binary)
            binary_index = binaries_absolute_path.index(binary)

            dependencies = list_dependencies(binary, arch)

            for dependency in dependencies:
                dependency = dependency.split(" => ")[1].split(" (")[0]

                if dependency not in binaries_absolute_path:
                    binaries_absolute_path.append(dependency)

                dependency_index = binaries_absolute_path.index(dependency)

                if binary_index not in binaries_index_to_dependencies_index:
                    binaries_index_to_dependencies_index[binary_index] = list()

                binaries_index_to_dependencies_index[binary_index].append(dependency_index)

from pyvis.network import Network

network = Network(width="100%", height="3000px")
# network.toggle_physics(status=True)
# network.toggle_stabilization(status=True)
network.barnes_hut()

for binary_absolute_path in binaries_absolute_path:
    binary_index = binaries_absolute_path.index(binary_absolute_path)
    network.add_node(binary_index, binary_absolute_path)

    if binary_index in binaries_index_to_dependencies_index:
        dependencies_indexes = binaries_index_to_dependencies_index[binary_index]

        for dependency_index in dependencies_indexes:
            dependency_absolute_path = binaries_absolute_path[dependency_index]
            network.add_node(dependency_index, dependency_absolute_path)
            network.add_edge(binary_index, dependency_index)

network.save_graph("index.html")