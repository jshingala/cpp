#include <iostream>
using namespace std;
void pattern(int n) {
    for (int i = 0; i <n; i++){ 
        for(int j= 0 ; j<(n-i) -1;j++){ cout <<" ";}
          for(int k=0;k<=i *2  ;k++){
                cout<< "*";
           }cout<<endl;
     }
    for (int i = 0; i < n - 1; i++) {
        // Spaces
        for (int j = 0; j <= i; j++) {
            cout << " ";
        }

        // Stars
        for (int k = 0; k < 2 * (n - i) - 3; k++) {
            cout << "*";
        }

        cout << endl;
    }
}
        



int main() {
    int n;
    cin >> n;
    pattern(n);
    return 0;
}