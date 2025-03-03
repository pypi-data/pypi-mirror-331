import h5py


def create_hdf5_from_json(structure, file_path):
    with h5py.File(file_path, "r+") as f:
        create_group(f, None, structure)


def create_group(parent_group, group_name, structure):
    if group_name is None:
        group = parent_group
    else:
        if group_name in parent_group:
            del parent_group[group_name]
        group = parent_group.create_group(group_name)
    for key, value in structure.items():
        if isinstance(value, dict):
            create_group(group, key, value)
        else:
            if value is None:
                value = "None"
            create_dataset(group, key, value)


def create_dataset(group, key, value):
    group.create_dataset(key, data=value)


def read_hdf5_group_to_dict(fp, group, is_file=False):
    if is_file:
        with h5py.File(fp, "r") as f:
            return recursively_load_dict(f[group])
    else:
        return recursively_load_dict(fp[group])


def recursively_load_dict(group):
    output = {}
    for key, val in group.items():
        if isinstance(val, h5py.Dataset):
            output[key] = val[...]
        elif isinstance(val, h5py.Group):
            output[key] = recursively_load_dict(val)
    return output
