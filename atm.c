#include <stdio.h>
#include <string.h>
#include <stdlib.h>
typedef struct {
    int accountNumber;
    int pin;
    float balance;
} Account;


Account accounts[] = {
    {123456, 1234, 0.00},
    {789012, 5678, 500.75},
    {345678, 9012, 2500.00}
};
int numAccounts = sizeof(accounts) / sizeof(accounts[0]);
int authenticateUser(int accountNumber, int pin) {
    for (int i = 0; i < numAccounts; i++) {
        if (accounts[i].accountNumber == accountNumber && accounts[i].pin == pin) {
            return i;
        }
    }
    return -1;
}

int main() {
    int choice;
    int accountNumber, pin, accountIndex = -1;
    float withdrawAmount, depositAmount;
    char continueTransaction = 'y';

    printf("Welcome to the ATM!\n");
    printf("Enter your Account Number: ");
    if (scanf("%d", &accountNumber) != 1) {
         printf("Invalid input for account number.\n");
         return 1;
    }

    printf("Enter your PIN: ");
     if (scanf("%d", &pin) != 1) {
         printf("Invalid input for PIN.\n");
         return 1;
    }

    accountIndex = authenticateUser(accountNumber, pin);

    if (accountIndex == -1) {
        printf("Authentication failed. Invalid account number or PIN.\n");
        return 1;
    }

    printf("\nAuthentication Successful!\n");
    do {

        printf("\n--------------------\n");
        printf("Account: %d\n", accounts[accountIndex].accountNumber);
        printf("Select an option:\n");
        printf("1. Withdraw\n");
        printf("2. Deposit\n");
        printf("3. Balance Check\n");
        printf("4. Exit\n");
        printf("--------------------\n");
        printf("Enter your choice: ");
        if (scanf("%d", &choice) != 1) {
             printf("\nInvalid input. Please enter a number (1-4).\n");
             while (getchar() != '\n');
             continue;
        }


        switch (choice) {
            case 1:
                printf("\nEnter the amount to withdraw: ");
                 if (scanf("%f", &withdrawAmount) != 1)
                    {
                    printf("Invalid amount entered.\n");
                    while (getchar() != '\n');
                    break;
                 }

                if (withdrawAmount <= 0)
                    {
                    printf("Withdrawal amount must be positive.\n");
                } else if (accounts[accountIndex].balance >= withdrawAmount)
                {
                    accounts[accountIndex].balance -= withdrawAmount;
                    printf("\nWithdrawal successful.");
                    printf("\nCurrent Balance: %.2f\n", accounts[accountIndex].balance);
                } else
                 {
                    printf("\nInsufficient balance.\n");
                    printf("Your balance is: %.2f\n", accounts[accountIndex].balance);
                }
                break;

            case 2:
                printf("\nEnter the amount to deposit: ");
                 if (scanf("%f", &depositAmount) != 1)
                    {
                    printf("Invalid amount entered.\n");
                    while (getchar() != '\n');
                    break;
                 }

                if (depositAmount <= 0)
                    {
                    printf("Deposit amount must be positive.\n");
                } else
                 {
                    accounts[accountIndex].balance += depositAmount;
                    printf("\nDeposit successful.");
                    printf("\nCurrent Balance: %.2f\n", accounts[accountIndex].balance);
                }
                break;

            case 3:
                printf("\nYour current balance is: %.2f\n", accounts[accountIndex].balance);
                break;

            case 4:
                printf("\nThank you for using the ATM. Exiting.\n");
                continueTransaction = 'n';
                break;

            default:
                printf("\nInvalid choice. Please enter a number between 1 and 4.\n");
                break;
        }
        if (continueTransaction != 'n' && choice != 4)
            {
             printf("\nDo you want to perform another transaction? (y/n): ");
             while (getchar() != '\n');
             scanf(" %c", &continueTransaction);
        }

    }
    while (continueTransaction == 'y' || continueTransaction == 'Y');

    printf("\nFinal session balance for account %d: %.2f (This will reset on next run)\n",
           accounts[accountIndex].accountNumber, accounts[accountIndex].balance);
    printf("Goodbye!\n");

    return 0;
}
