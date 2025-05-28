global_DATA_PATH = 'advanced_tracking/';

load_trackers(path) ->(print('loading'));

load_data(path) ->(
    if(slice(path, length(path)-1) != '/', path += '/');
    global_tracking_data = {};
    file_lst = list_files(path, 'shared_json');
    print(file_lst);
    for(file_lst, (
        path = _;
        name = slice(_, length(path));
        global_tracking_data:name = read_file(path, 'shared_json');
    ));
);

save_data(path) -> (
    if(slice(path, length(path)-1) != '/', path += '/');
    for(global_tracking_data, (
        uuid=_;
        write_file(path+uuid, 'shared_json', global_tracking_data:uuid)
    ));
);

check_player_in_area(pos, area) -> (
    if(area:'x_min' != null, if(area:'x_min' > x, return(false)));
    if(area:'x_max' != null, if(area:'x_max' < x, return(false)));
    
    if(area:'y_min' != null, if(area:'y_min' > y, return(false)));
    if(area:'y_max' != null, if(area:'y_max' < y, return(false)));
    
    if(area:'z_min' != null, if(area:'z_min' > z, return(false)));
    if(area:'z_max' != null, if(area:'z_max' < z, return(false)));
    return(true);
);