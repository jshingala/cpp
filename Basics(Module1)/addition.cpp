#include <iostream>
using namespace std;

int sum(int num1, int num2){
    int num3= num2+num1;
    return num3;
}
void nums(int nums){
    cout <<nums<<"\n";
    nums += 5;
    cout << num << endl;
    
}

int main(){
    int num1, num2;
    cin >> num1>> num2;
    int res= sum(num1, num2);
    cout << res;

    int nums= 10
    doSomething(nums);
    return 0;
}