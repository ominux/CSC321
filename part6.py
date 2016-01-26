from part2 import fetch_sets
from k_nearest_neighbors import knn_classify
from distance_functions import euclidean_distance
from scipy.misc import imresize
from collections import defaultdict
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import os
import shutil
import sys

if len(sys.argv) == 3:
    save_ext = sys.argv[1]
    plot_graphs = (sys.argv[2] == '1')
else:
    save_ext = 'eps'
    plot_graphs = False

plt.gray()
if os.path.exists("results/part_6/k_sensitivity"):
    shutil.rmtree("results/part_6/k_sensitivity")
os.makedirs("results/part_6/k_sensitivity")
if os.path.exists("results/part_6/mislabels"):
    shutil.rmtree("results/part_6/mislabels")
os.makedirs("results/part_6/mislabels")

x_train_f = fetch_sets("subset_actresses.txt", ['Lorraine Bracco', 'Peri Gilpin', 'Angie Harmon'], 100, 0, 0)[0]
x_train_m = fetch_sets("subset_actors.txt", ['Gerard Butler', 'Daniel Radcliffe', 'Michael Vartan'], 100, 0, 0)[0]

_, _, x_validation_f, _, x_test_f, _ = fetch_sets("subset_actresses.txt", ['Carmen Electra', 'Kim Cattrall', 'Loni Anderson'], 0, 10, 10)
_, _, x_validation_m, _, x_test_m, _ = fetch_sets("subset_actors.txt", ['Chris Klein', 'Leonardo DiCaprio', 'Jason Statham'], 0, 10, 10)

genders = ['Male', 'Female']
x_train = x_train_f + x_train_m
t_train = np.hstack((np.ones(len(x_train_f)), np.zeros(len(x_train_m))))

x_validation = x_validation_f + x_validation_m
t_validation = np.hstack((np.ones(len(x_validation_f)), np.zeros(len(x_validation_m))))

x_test = x_test_f + x_test_m
t_test = np.hstack((np.ones(len(x_test_f)), np.zeros(len(x_test_m))))

min_dim = min(map(np.shape, x_train+x_validation+x_test))

xto = np.array(x_train)
xteo = np.array(x_test)

x_train = np.array([np.hstack(imresize(x, (32,32))) for x in x_train])
x_validation = np.array([np.hstack(imresize(x, (32,32))) for x in x_validation])
x_test = np.array([np.hstack(imresize(x, (32,32))) for x in x_test])

krange = [i for j in (range(1,10), range(11, len(x_train),5), [len(x_train)]) for i in j]
validation_errors = np.zeros(len(krange))
validation_distances = defaultdict(list)
for j, k in enumerate(krange):
    for i, xi in enumerate(x_validation):
        ti, _ = knn_classify(x_train, t_train, xi, k, euclidean_distance, validation_distances[i])

        if ti != t_validation[i]:
            validation_errors[j] += 1
    print "K = %d - Validation Errors = %d (%d%%)" %(k, validation_errors[j], validation_errors[j]/len(x_validation)*100)

best_ki = np.where(validation_errors == validation_errors.min())[0]
best_k = np.array(krange)[best_ki]
best_perf = validation_errors[best_ki]/len(x_validation)*100
np.savetxt("results/part_6/eval_performance.csv", np.array(zip(best_k, best_perf)), fmt='%i %i')
print "Best values for k: %s\n" %best_k

test_errors = np.zeros(len(best_k))
test_distances = defaultdict(list)
trigger = 0
nl=0
for j, k in enumerate(best_k):
    for i, xi in enumerate(x_test):
        ti, _ = knn_classify(x_train, t_train, xi, k, euclidean_distance, test_distances[i])
        if ti != t_test[i]:
            test_errors[j] += 1

            if trigger % 2 == 0:
                _, nn = knn_classify(x_train, t_train, xi, 5, euclidean_distance, test_distances[i])
                plt.suptitle(genders[int(t_test[i])], size=20)
                plt.subplot(1,2,1)
                plt.imshow(xteo[i])
                plt.title(genders[int(ti)], color='red')
                plt.axis('off')
                for n, m in enumerate([3,4,7,8,11]):
                    plt.subplot(3,4,m)
                    plt.imshow(xto[nn[n]])
                    if t_train[nn[n]] != t_test[i]:
                        plt.title(genders[int(t_train[nn[n]])], color='red')
                    else:
                        plt.title(genders[int(t_train[nn[n]])], color='green')
                    plt.axis('off')
                plt.savefig('results/part_6/mislabels/%d.%s' %(nl, save_ext), bbox_inches='tight')
                nl+=1
                plt.close()
            trigger += 1
    print "K = %d - Test Errors = %d (%d%%)" %(k, test_errors[j], test_errors[j]/len(x_test)*100)

best_k_ti = np.where(test_errors == test_errors.min())[0]
best_k_t = best_k[best_k_ti]
best_perf = validation_errors[best_k_ti]/len(x_test)*100
np.savetxt("results/part_6/test_performance.csv", np.array(zip(best_k_t, best_perf)), fmt='%i %i')
print "Best values for k: %s" %best_k_t

font = {'size' : 15}
matplotlib.rc('font', **font)
plt.axis('on')
plt.plot([i for i in krange], validation_errors/len(x_validation)*100, label='Validation Set', marker='o')
plt.scatter([i for i in best_k], test_errors/len(x_test)*100, label='Test Set', marker='*', s=150, color='r')
plt.xlabel('Neighbors Considered')
plt.ylabel('% of Classification Errors')
plt.title('K Sensitivity Test')
plt.axis([-10, len(x_train), 0, 100])
plt.legend(loc=0)
plt.grid()
plt.savefig('results/part_6/k_sensitivity/k_sensitivity.%s' %(save_ext), bbox_inches='tight')
plt.show() if plot_graphs else plt.close()