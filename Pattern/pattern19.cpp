#include <iostream>
using namespace std;

void pattern(int n) {
    
    for(int i =0; i<n;i++){ //rows
        int space = 2*i;
        for(int k =0;k <n-i;k++ ) cout<<"*"; // For first Iteration Of pattern
        for(int j= 0; j<space;j++) cout<< " ";//For Space Before Colown 2nd iternation
        for(int l=0; l<n-i;l++) cout<<"*"; // for Second Iteration
        cout << endl;
    }
    for(int i=0; i<n;i++){
        for(int k=0; k<=i;k++) cout<<"*";
        int space= 2*(n-i-1); //for first iteration;
        for(int j=0;j<space;j++)cout<<" "; //for spaces;
        space -=2;
        for(int l= 0;l<=i;l++)cout<< "*";
        
        cout<<endl;
    }

}


int main() {
    int n;
    cin >> n;
    pattern(n);
    return 0;
}