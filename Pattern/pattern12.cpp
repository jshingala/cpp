#include <iostream>
using namespace std;
void pattern(int n) {
    int space= 2*(n-1);
    for (int i =1; i  <=n; i++){
        for (int j=1; j<= i; j++)cout << j;
        for(int k =1 ; k<=space;k++)cout<<" ";
        for (int l= i;l>=1; l--)cout <<l;
        cout<< endl;
        space -=2;
    }
}
        



int main() {
    int n;
    cin >> n;
    pattern(n);
    return 0;
}