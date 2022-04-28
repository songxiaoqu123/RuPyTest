def write_list_2D_to_file(list_2D, filename):
    with open(filename,'w') as f:
        for i in range(len(list_2D)):
            for j in list_2D[i]:
                f.write(j)
                f.write('\t\t')
            f.write('\n')
