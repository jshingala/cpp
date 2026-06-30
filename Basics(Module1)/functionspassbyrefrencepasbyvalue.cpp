#include <iostream>
using namespace std;

void printName(string name){
    cout<< "The main reason " << name << "\n";
}
int main(){
    string name, name2;
    cin >> name;
    printName(name);
    // can reuse the code
    cin >> name2;
    printName(name2);
    return 0;
}

