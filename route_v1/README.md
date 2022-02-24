# route_v1
* [route_alloc_1.txt](route_alloc_1.txt) has larger dataset
* [data.py](data.py) selects specified number of rows (*4 vehicles and 48 consignments currently*) from [route_alloc_1.txt](route_alloc_1.txt) and prints them in file [inpt1.txt](inpt1.txt)
* [route_v1.py](route_v1.py) takes input from file [inpt1.txt](inpt1.txt) and prints in terminal; example output shown in file [otpt.txt](otpt.txt)

### otpt.txt
    Vehicle <vehicle id>
    <number of consignments> <consignment ids>
    <consignment id> <P/D> <latitude> <longitude>
    .
    .
    Vehicle ...
