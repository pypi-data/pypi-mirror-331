import os
import inspect

# Define named sections (grouped by subjects)
CODE_SECTIONS = {
    "linear_regression": """

p1
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

data = pd.read_csv('Salary_data.csv')
data.head()
x,y = data['YearsExperience'], data ['Salary']

B1 = ((x-x.mean())* (y-y.mean())).sum() / ((x-x.mean())**2).sum()
B0 = y.mean() -B1  * x.mean()
R = np.corrcoef(x,y)[0,1]

print(f'Regression Line: Y {round(B0,3)} + {round(B1,3)}x')
print(f'Correation: {round(R,4)}, R^2: {round(R**2,4)}')

plt.scatter(x,y,s=300,edgecolor='black')
plt.plot(x, B0+B1*x, c = 'r', linewidth = 5)
plt.text(1,100000,
        f'Mean X: {round(x.mean(),2)}, Mean Y: {round(y.mean(),2)},\nR: {round(R,4)}, R^2: {round(R**2,4)}',
        fontsize=12, bbox={'facecolor':'grey', 'alpha':0.2,'pad': 10})
plt.title('Experience vs Salary')
plt.xlabel('Experience')
plt.ylabel('Salary')
plt.show()
print("saalry for 70 Yrs Experience: ",(B0+B1*70))

""",

    "logistics_regression": """
p2
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn import metrics

data = pd.read_csv('Admission_Data.csv')
x = data[['gmat', 'gpa', 'work_experience']]
y = data['admitted']
print(data.head(10))
x_train,x_test,y_train,y_test = train_test_split(x,y,test_size=0.25, random_state=0)

model = LogisticRegression().fit(x_train,y_train)
y_pred = model.predict(x_test)

print(pd.crosstab(y_test,y_pred,rownames=['Actual'],colnames=['Pridcted']))
print("Accuracy: ",metrics.accuracy_score(y_test,y_pred))

""",

    "time_serise": """

p3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

data = pd.read_csv('AirPassengers.csv')
data['Month'] = pd.to_datetime(data['Month'], format='%Y-%m')
data.set_index('Month', inplace = True)

print(data.head(), data.tail())

sns.lineplot(data= data, x = 'Month', y = '#Passengers')
plt.title('Number of Air Passenegrs')
plt.ylabel('number of Passengers')
plt.show()

""",

    "native_bayes": """

p4
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
weather=['sunny','sunny','overcast','rainy','rainy','rainy','overcast','sunny','sunny','rainy','sunny','overcast','overcast','rainy']
temp=['hot','hot','hot','mild','cool','cool','cool','mild','cool','mild','mild','mild','hot','mild']
play=['no','no','yes','yes','yes','no','yes','no','yes','yes','yes','yes','yes','no']
from sklearn import preprocessing as p
le=p.LabelEncoder()
weather_encode=le.fit_transform(weather)
print(weather_encode)
temp_encode=le.fit_transform(temp)
label=le.fit_transform(play)
print('Temp: ',temp_encode)
print('Play: ',label)

""",

    "k_means": """

p5
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans

sns.set()

data = pd.read_csv('CountryClusters.csv')
data.head()
plt.scatter(data['Longitude'], data['Latitude'])
plt.xlim(-180,180)
plt.ylim(-90,90)
plt.show()

kmeans = KMeans(3).fit(data.iloc[:,1:3])
data['clusters'] = kmeans.labels_

plt.scatter(data['Longitude'], data['Latitude'],c=data['clusters'],cmap='rainbow')
plt.show()



""",

    "principle_component": """
p6
import numpy as np
from sklearn.decomposition import PCA

x = np.array([[-1,-1], [-2,-1], [-3,-2], [1,1], [2,1], [3,2]])

for n_components, solver in [(2,'auto'), (2,'full'), (1,'arpack')]:
    pca = PCA(n_components = n_components, svd_solver = solver)
    pca.fit(x)
    print(f'Components: {n_components}, solver: {solver}')
    print("Explained Varience: ",pca.explained_variance_ratio_)
    print("Singular Value: ", pca.singular_values_,"\n")

""",

    "decision_tree": """

p7a
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

data = pd.read_csv('iris.csv')
data.columns = data.columns.str.strip()

x = data.iloc[:, 0:4].values
y = LabelEncoder().fit_transform(data['variety'])

x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=0)

model = DecisionTreeClassifier(criterion='entropy', random_state=0)
model.fit(x_train, y_train)

y_pred = model.predict(x_test)

print(f"\nAccuracy: {accuracy_score(y_test, y_pred) * 100:.2f}%")
print("\nClassification Report:\n", classification_report(y_test, y_pred))

sns.heatmap(confusion_matrix(y_test, y_pred), annot=True, cmap='Blues', fmt='d')
plt.title("Confusion Matrix")
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.show()

plt.figure(figsize=(12, 8))
plot_tree(model, feature_names=data.columns[0:4], class_names=data['variety'].unique(), filled=True)
plt.title("Decision Tree")
plt.show()


""",
    "diabetes": """

p7b
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.metrics import accuracy_score

data = pd.read_csv("diabetes.csv")
X, y = data.iloc[:, :-1], data.iloc[:, -1]
X_scaled = StandardScaler().fit_transform(X)

def impurity_measures(y):
    _, counts = np.unique(y, return_counts=True)
    prob = counts / len(y)
    return -np.sum(prob * np.log2(prob)), 1 - np.sum(prob**2)

entropy, gini = impurity_measures(y)
print(f"\nEntropy: {entropy:.4f}, Gini Index: {gini:.4f}")

X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=0)

tree_model = DecisionTreeClassifier(criterion='gini', max_depth=4, random_state=0).fit(X_train, y_train)

print(f"\nTest Accuracy: {accuracy_score(y_test, tree_model.predict(X_test)) * 100:.2f}%")

plt.figure(figsize=(20, 10))
plot_tree(tree_model, feature_names=data.columns[:-1], class_names=["No Diabetes", "Diabetes"], filled=True, rounded=True)
plt.title("Decision Tree for Diabetes Classification")
plt.show()



""",
    "contrast_stretching": """
p8 
import pandas as pd
from apyori import apriori

data = pd.read_csv('store_data.csv', header=None)
data.head()
records= []

for i in range(0,7501):
    records.append([str(data.values[i,j])for j in range(0,20)])

a_rule = apriori(records, min_support= 0.0045, min_confidence = 0.2, min_lift = 3, min_length=2)
a_r = list(a_rule)
print(len(a_r))
print(a_r)

"""

}

# Mapping multiple names (aliases) to sections
SECTION_ALIASES = {
    "1": "linear_regression",
    "regression": "linear_regression",
    "2": "logistic_regression",
    "logistic": "logistic_regression",
    "3": "time_serise",
    "line_plot": "time_serise",
    "4": "native_bayes",
    "label_encoder": "native_bayes",
    "5": "k_means",
    "clustring": "k_means",
    "k-means": "k_means",
    "6": "principle_component",
    "principal_component": "principle_component",
    "pca": "principle_component",
    "PCA": "principle_component",
    "7a": "decision_tree",
    "7b": "diabetes",
    "decision": "decision_tree",
    "tree": "decision_tree",
    "iris": "decision_tree",
    "8": "contrast_stretching",
    "apriori": "contrast_stretching"

}
# Define subject-wise organization
SUBJECT_SECTIONS = {
    "all": {
        "sections": ["linear_regression","logistic_regression","time_serise","native_bayes","k_means","principle_component",
                     "decision_tree","diabetes","contrast_stretching"]
    }
}

def get_importing_script():
    """Find the actual script that imports this package."""
    for frame in reversed(inspect.stack()):
        filename = frame.filename
        if filename.startswith("<") or "idlelib" in filename or "run.py" in filename:
            continue
        return os.path.abspath(filename)
    return None

def code(section_name):
    """Pastes the specified section(s) into the importing script."""
    importing_script = get_importing_script()
    
    if not importing_script or not os.path.isfile(importing_script):
        print(f"❌ Error: Unable to find the target script.")
        return
    
    with open(importing_script, "a") as target_file:
        if section_name in SUBJECT_SECTIONS:
            # "all1" or "all2" detected, paste subject-wise
            subject_info = SUBJECT_SECTIONS[section_name]
            sections = subject_info["sections"]
            
            for sec_name in sections:
                if sec_name in CODE_SECTIONS:
                    target_file.write("\n\n#  {} ---\n".format(sec_name))
                    target_file.write(CODE_SECTIONS[sec_name])
        else:
            # Check if section name is an alias
            actual_section = SECTION_ALIASES.get(section_name, section_name)

            if actual_section not in CODE_SECTIONS:
                print(f"❌ Error: Section '{section_name}' not found.")
                return
            
            # Paste the specific section
            target_file.write(CODE_SECTIONS[actual_section])