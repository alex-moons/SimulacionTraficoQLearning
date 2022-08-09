#include <string>
#include <iostream>
#include <regex>

using namespace std;

int main(){
    int nDesigners;
    string pName,desc;

    cin>>nDesigners;
    if ((nDesigners>= 0) && (nDesigners>=200000)){
        cout<<"Error, designer's not within limit"<<endl;
        exit(1);
    }
    
    cin>>pName;
    
    for (int i = 0; i < nDesigners; i++){
        getline(cin, desc);
        pName.replace(pName.find(desc[0]),1,desc[2]);
        cout<<pName<<endl;
    }
}