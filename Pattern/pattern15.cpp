#include <iostream>
using namespace std;
void pattern(int n) {
    char ch= 'A';
    for (int i =0; i  <=n; i++){
        for (int j= 1; j<= n-i; j++)cout <<ch++;
        ch= 'A';
        cout<<endl;
}}



int main() {
    int n;
    cin >> n;
    pattern(n);
    return 0;
}